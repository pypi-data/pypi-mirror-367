import os
import glob
import pickle
import mrcfile
import numpy as np
import tifffile
import time
import json
from Pom.core.util import *
import copy
from Pom.core.config import project_configuration, FeatureLibraryFeature, feature_library, parse_feature_library
import shutil
import starfile


def phase_1_initialize():
    from Ais.core.se_frame import SEFrame

    os.makedirs(os.path.join(project_configuration['root'], "training_datasets"), exist_ok=True)
    os.makedirs(os.path.join(project_configuration['root'], "training_datasets", "phase1"), exist_ok=True)
    #os.makedirs(os.path.join(project_configuration['root'], "training_datasets", "phase1", "counter"), exist_ok=True)

    data = dict()
    n_annotated_tomos = dict()
    for o in project_configuration['ontologies']:
        n_annotated_tomos[o] = 0
        data[o] = dict()
        data[o]['y'] = list()
        for m in project_configuration['macromolecules']:
            data[o][m] = list()

    print(f"Looking for .scns files at {os.path.join(project_configuration['root'], project_configuration['tomogram_dir'], '*.scns')}")
    annotated_datasets = glob.glob(os.path.join(project_configuration['root'], project_configuration['tomogram_dir'], "*.scns"))
    print(f"Found {len(annotated_datasets)} .scns files.")

    for j, scns in enumerate(annotated_datasets):
        print(f"Annotated dataset {j+1}/{len(annotated_datasets)}: {os.path.basename(scns)}")
        try:
            with open(scns, 'rb') as pf:
                se_frame = pickle.load(pf)
        except Exception as e:
            print(f"\terror loading {j}\n\t{e}")
            continue
        tomo_name = os.path.splitext(os.path.basename(scns))[0]
        macromolecules = dict()
        all_macromolecules_found = True
        for m in project_configuration["macromolecules"]:
            if m == "Density":
                path = os.path.join(project_configuration['root'], project_configuration['tomogram_dir'], tomo_name + f".mrc")
            else:
                path = os.path.join(project_configuration['root'], project_configuration["macromolecule_dir"], tomo_name + f"__{m}.mrc")
            if not os.path.exists(path):
                print(f"Expected {path} but it does not exist, skipping {scns}.")
                all_macromolecules_found = False
                continue
            macromolecules[m] = mrcfile.mmap(path)
        if not all_macromolecules_found:
            continue
        for feature in se_frame.features:
            o = feature.title
            if o not in project_configuration['ontologies']:
                print(f"Skipping:\t{o} ")
                continue
            n_annotated_tomos[o] += 1
            print(f"Parsing:\t{o}")
            for z in feature.boxes.keys():
                for (j, k) in feature.boxes[z]:
                    j_min = (j - project_configuration['ontology_annotation_box_size'] // 2)
                    j_max = (j + project_configuration['ontology_annotation_box_size'] // 2)
                    k_min = (k - project_configuration['ontology_annotation_box_size'] // 2)
                    k_max = (k + project_configuration['ontology_annotation_box_size'] // 2)
                    if z in feature.slices and feature.slices[z] is not None and (z > project_configuration['z_sum']) and (z < se_frame.n_slices - project_configuration['z_sum']):
                        annotation = feature.slices[z][k_min:k_max, j_min:j_max]
                        if annotation.shape == (project_configuration['ontology_annotation_box_size'], project_configuration['ontology_annotation_box_size']):
                            data[o]['y'].append(bin_img(annotation, 2))
                            for m in macromolecules:
                                m_vol = macromolecules[m].data[z - project_configuration['z_sum']:z + project_configuration['z_sum'] + 1, k_min:k_max, j_min:j_max]
                                m_img = bin_img(m_vol.mean(0), 2)
                                if m == "Density":
                                    m_img -= np.mean(m_img)
                                    _std = np.std(m_img)
                                    if _std != 0.0:
                                        m_img /= np.std(m_img)
                                else:
                                    m_img = m_img / 255.0 * 2.0 - 1.0
                                data[o][m].append(m_img)

    print()

    # Save the data.
    for o in data:
        n_annotated = 0
        if len(data[o]['y']) == 0:
            continue
        for m in data[o]:
            dataset = np.array(data[o][m])
            tifffile.imwrite(os.path.join(project_configuration['root'], "training_datasets", "phase1", f"{o}_{m}.tif"), dataset)
            if m == 'y':
                n_annotated = np.sum(np.sum(dataset, axis=(1, 2)) != 0)
        print(f"{o}:{' '*(35 - len(o))}{dataset.shape[0]} training images (of which {n_annotated} annotated, {dataset.shape[0] - n_annotated} not) across {n_annotated_tomos[o]} volumes.")

    print()

    # Save all boxes where annotation is full 1's, as extra negative examples for other classes
    # for o in data:
    #     n_full_o_images = 0
    #     counter_data = dict()
    #     counter_data['y'] = list()
    #     for m in project_configuration["macromolecules"]:
    #         counter_data[m] = list()
    #     for j in range(len(data[o]['y'])):
    #         annotation = data[o]['y'][j]
    #         if 0.0 not in annotation:
    #             n_full_o_images += 1
    #             counter_data['y'].append(np.zeros_like(annotation))
    #             for m in project_configuration["macromolecules"]:
    #                 counter_data[m].append(data[o][m][j])
    #     if n_full_o_images > 0:
    #         for m in counter_data:
    #             dataset = np.array(counter_data[m])
    #             tifffile.imwrite(os.path.join(project_configuration["root"], "training_datasets", "phase1", "counter", f"{o}_{m}.tif"), dataset)
    #         print(f"{o}:{' '*(35 - len(o))}{dataset.shape[0]} counter-training images.")

    print(f"Training datasets generated and saved to: \t/{os.path.join(project_configuration['root'], 'training_datasets')}")


def phase_1_train(gpus, ontology, use_counterexamples=0, all_features=0):
    # TODO: save models as Ais .scnm files!
    if all_features == 1:
        for f in project_configuration["ontologies"]:
            phase_1_train(gpus=gpus, ontology=f, use_counterexamples=use_counterexamples, all_features=0)
        return

    import tensorflow as tf
    import keras.callbacks
    from Pom.models.phase1model import create_model
    from Ais.core.se_model import SEModel

    os.environ["CUDA_VISIBLE_DEVICES"] = gpus

    os.makedirs(os.path.join(project_configuration["root"], "models", "phase1"), exist_ok=True)
    os.makedirs(os.path.join(project_configuration["root"], "training_datasets", "phase1"), exist_ok=True)

    def add_redundancy(data):
        data_out = list()
        for img in data:
            for k in [0, 1, 2, 3]:
                _img = np.rot90(img, k, axes=(0, 1))
                data_out.append(_img)
                data_out.append(np.flip(_img, axis=0))
        return np.array(data_out)

    def load_data():
        data = dict()
        for m in ['mask', 'y'] + project_configuration['macromolecules']:
            data[m] = list()

        valid_images = list()
        for o in project_configuration['ontologies']:
            if not use_counterexamples and o != ontology:
                continue
            for m in ['y'] + project_configuration['macromolecules']:
                data[m].append(tifffile.imread(os.path.join(project_configuration['root'], "training_datasets", "phase1", f"{o}_{m}.tif")).astype(np.float32))
            o_shape = data['y'][-1].shape
            if o == ontology:
                data['mask'].append(np.ones(o_shape))
                valid_images.append(np.ones(o_shape[0]))  # here, un-annotated images are guaranteed to be valid.
            else:
                data['mask'].append(data['y'][-1])
                valid_images.append(np.zeros(o_shape[0]))  # here, un-annotated regions are NOT guaranteed NOT to be the chosen feature.

        for m in ['mask', 'y'] + project_configuration['macromolecules']:
            data[m] = np.concatenate(data[m])

        data_y = data['y']
        data_m = data['mask']
        data_x = np.zeros((*data_y.shape, len(project_configuration['macromolecules'])), dtype=np.float32)

        for j, m in enumerate(project_configuration['macromolecules']):
            data_x[:, :, :, j] = data[m]

        valid_images = np.concatenate(valid_images)
        valid_images = (valid_images + np.sum(data_m, axis=(1, 2))) > 0  # if guaranteed valid OR mask is not all zeroes -> use in training

        data_y = data_y[valid_images, :, :]
        data_m = data_m[valid_images, :, :]
        data_x = data_x[valid_images, :, :, :]
        return data_x, data_y, data_m

    data_x, data_y, data_m = load_data()
    data_x = add_redundancy(data_x)
    data_y = add_redundancy(data_y)
    data_m = add_redundancy(data_m)

    def tf_data_generator():
        n_samples = data_x.shape[0]
        indices = np.arange(n_samples)

        while True:
            np.random.shuffle(indices)
            for i in range(0, n_samples, project_configuration['single_model_batch_size']):
                batch_indices = indices[i:i + project_configuration['single_model_batch_size']]
                batch_x = data_x[batch_indices]
                batch_y = np.stack([data_y[batch_indices], data_m[batch_indices]], axis=-1)
                yield batch_x, batch_y

    training_data = tf.data.Dataset.from_generator(tf_data_generator, output_signature=(tf.TensorSpec(shape=(None, data_x.shape[1], data_x.shape[2], data_x.shape[3]), dtype=tf.float32), tf.TensorSpec(shape=(None, data_y.shape[1], data_y.shape[2], 2), dtype=tf.float32)))
    options = tf.data.Options()
    options.experimental_distribute.auto_shard_policy = tf.data.experimental.AutoShardPolicy.DATA
    training_data = training_data.with_options(options)

    strategy = tf.distribute.get_strategy() if not project_configuration['tf_distribute_mirrored'] else tf.distribute.MirroredStrategy()
    with strategy.scope():
        model = create_model(data_x.shape[1:], output_dimensionality=1)

    print(f"Training a model for {ontology} with inputs:")
    [print(f"\t{m}") for m in project_configuration['macromolecules']]
    print(f"and {data_y.shape[0]} training images.")

    checkpoint_callback = keras.callbacks.ModelCheckpoint(filepath=os.path.join(project_configuration['root'], "models", "phase1", f"{ontology}_checkpoint.h5"), monitor='loss', mode='min', save_best_only=True)
    model.fit(training_data, epochs=project_configuration['single_model_epochs'], steps_per_epoch=data_x.shape[0] // project_configuration['single_model_batch_size'], shuffle=True, callbacks=[checkpoint_callback])
    shutil.move(os.path.join(project_configuration["root"], "models", "phase1", f"{ontology}_checkpoint.h5"), os.path.join(project_configuration["root"], "models", "phase1", f"{ontology}.h5"))
    se_model = SEModel()
    se_model.title = ontology
    se_model.model = model
    se_model.save(os.path.join(project_configuration["root"], "models", "phase1", f"{ontology}.scnm"))
    print(f'Saved: {os.path.join(project_configuration["root"], "models", "phase1", f"{ontology}.h5")} and *.scnm (for testing in Ais)')


def phase_1_test(gpus, ontology, process=True):
    import tensorflow as tf
    import multiprocessing
    import itertools
    from scipy.ndimage import convolve1d
    from Pom.models.phase1model import create_model

    def preprocess_volume(vol):
        return bin_vol(convolve1d(vol, np.ones(2 * project_configuration["z_sum"] + 1) / (2 * project_configuration["z_sum"] + 1), axis=0, mode='nearest'), 2)

    def segment_tomo(tomo, model):
        components = dict()

        tomo_name = os.path.splitext(os.path.basename(tomo))[0]
        for m in project_configuration["macromolecules"]:
            if m == 'Density':
                components[m] = preprocess_volume(mrcfile.read(os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], f"{tomo_name}.mrc")))
            else:
                components[m] = preprocess_volume(mrcfile.read(os.path.join(project_configuration["root"], project_configuration["macromolecule_dir"], f"{tomo_name}__{m}.mrc"))) / 255.0 * 2.0 - 1.0

        data_x = np.zeros((*components[project_configuration["macromolecules"][0]].shape, len(project_configuration["macromolecules"])), dtype=np.float32)
        for j, m in enumerate(components):
            data_x[:, :, :, j] = components[m]

        data_y = np.zeros(data_x.shape[0:3], dtype=np.float32)
        out_w = 32 * (data_y.shape[1] // 32)
        out_w_margin = (data_y.shape[1] % 32) // 2
        out_h = 32 * (data_y.shape[2] // 32)
        out_h_margin = (data_y.shape[2] % 32) // 2
        n_runs = max(min(4, project_configuration['shared_model_runs_per_volume']), 1)
        for j in range(data_y.shape[0]):
            slice_j = data_x[j, :, :, :]
            for k in range(n_runs):
                rotated_slice = np.rot90(slice_j, k=k, axes=(0, 1))
                w = 32 * (rotated_slice.shape[0] // 32)
                w_pad = (rotated_slice.shape[0] % 32) // 2
                h = 32 * (rotated_slice.shape[1] // 32)
                h_pad = (rotated_slice.shape[1] % 32) // 2
                data_y[j, out_w_margin:out_w_margin+out_w, out_h_margin:out_h_margin+out_h] += np.rot90(np.squeeze(model.predict(rotated_slice[w_pad:w_pad+w, h_pad:h_pad+h][np.newaxis, :, :])), k=-k, axes=(0, 1))
        data_y /= n_runs
        return data_y

    def _thread(model_path, tomogram_paths, gpu_id, process=False):
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

        output_directory = os.path.join(project_configuration["root"], project_configuration["test_dir"]) if not process else os.path.join(project_configuration["root"], project_configuration["output_dir"])
        os.makedirs(output_directory, exist_ok=True)
        inference_model = create_model((None, None, len(project_configuration["macromolecules"])), output_dimensionality=1)
        trained_model = tf.keras.models.load_model(model_path, compile=False)
        for nl, l in zip(inference_model.layers, trained_model.layers):
            nl.set_weights(l.get_weights())

        for j, tomo in enumerate(tomogram_paths):
            t_start = time.time()
            try:
                out_name = os.path.join(output_directory, os.path.basename(os.path.splitext(tomo)[0])+f"__{ontology}.mrc")
                vol_out = segment_tomo(tomo, inference_model)
                with mrcfile.new(out_name, overwrite=True) as f:
                    f.set_data(vol_out.astype(np.float32))
                    f.voxel_size = project_configuration["apix"] * 2
                print(f"(GPU {gpu_id}) {j+1}/{len(tomogram_paths)}: {ontology} cost: {time.time() - t_start:.1f} seconds.")
            except Exception as e:
                print(e)

    all_tomos = [p for p in glob.glob(os.path.join(project_configuration["root"], project_configuration["test_dir"], "*.mrc")) if not '__' in os.path.basename(p)]
    if process:
        all_tomos = [p for p in glob.glob(os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], "*.mrc")) if not '__' in os.path.basename(p)]
    _gpus = [int(j) for j in gpus.split(",")]
    data_div = {gpu: list() for gpu in _gpus}
    for gpu, tomo_path in zip(itertools.cycle(_gpus), all_tomos):
        data_div[gpu].append(tomo_path)

    processes = []
    for gpu_id in data_div:
        p = multiprocessing.Process(target=_thread, args=(os.path.join(project_configuration["root"], "models", "phase1", f"{ontology}.h5"), data_div[gpu_id], gpu_id, process))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()


def phase_2_initialize(selective=False):
    """
    :param selective: True to use only those images in the separate training datasets where at least 1 pixel was annotated.
    """
    import tensorflow as tf
    from scipy.ndimage import gaussian_filter
    import gc

    os.makedirs(os.path.join(project_configuration['root'], "training_datasets", "phase2"), exist_ok=True)

    def model_predict_with_redundancy(m_model, m_data_x):
        prediction = np.zeros((m_data_x.shape[0], m_data_x.shape[1], m_data_x.shape[2], 1))

        for k in [0, 1, 2, 3]:
            d = np.rot90(m_data_x, k=k, axes=(1, 2))
            _p = m_model.predict(d)
            p = np.rot90(_p, k=-k, axes=(1, 2))
            prediction += p

            d = np.flip(d, axis=2)
            _p = m_model.predict(d)
            p = np.rot90(np.flip(_p, axis=2), k=-k, axes=(1, 2))
            prediction += p
        prediction /= 8
        prediction = np.squeeze(prediction)
        return prediction

    macromolecule_inputs = project_configuration["macromolecules"]
    ontologies = project_configuration["ontologies"]

    data_x = list()
    data_y = list()
    data_m = list()
    for j, o in enumerate(ontologies):
        o_data_y = tifffile.imread(os.path.join(project_configuration["root"], "training_datasets", "phase1", f"{o}_y.tif"))
        o_data_x = np.zeros((*o_data_y.shape, len(macromolecule_inputs)))
        o_data_m = np.zeros((o_data_y.shape[0])) + j
        for k, m in enumerate(macromolecule_inputs):
            o_data_x[:, :, :, k] = tifffile.imread(os.path.join(project_configuration["root"], "training_datasets", "phase1", f"{o}_{m}.tif"))
        if selective:
            selection = list()
            for k in range(o_data_y.shape[0]):
                selection.append(np.sum(o_data_y[k, :, :])  > 0)

            o_data_y = o_data_y[selection, :, :]
            o_data_x = o_data_x[selection, :, :, :]
            o_data_m = o_data_m[selection]

        data_x.append(o_data_x)
        data_y.append(o_data_y)
        data_m.append(o_data_m)

    data_x = np.concatenate(data_x, axis=0)
    data_y = np.concatenate(data_y, axis=0)
    data_m = np.concatenate(data_m, axis=0)

    model_outputs = dict()
    for o in ontologies:
        model = tf.keras.models.load_model(os.path.join(project_configuration["root"], "models", "phase1", f"{o}.h5"), compile=False)
        print(f"Applying model {o} to training data.")
        model_outputs[o] = model_predict_with_redundancy(model, data_x)
        del model
        tf.keras.backend.clear_session()
        gc.collect()

    # Now parse into a joint dataset.
    for j, m in enumerate(macromolecule_inputs):
        out_tif = np.squeeze(data_x[:, :, :, j]).astype(np.float32)
        tifffile.imwrite(os.path.join(project_configuration["root"], "training_datasets", "phase2", f"in_{m}.tif"), out_tif)

    new_data_y = np.zeros((*data_y.shape, len(ontologies)+1))
    for j, o in enumerate(ontologies):
        print(f"Parsing new output for {o}")
        model_y = model_outputs[o]
        for k in range(model_y.shape[0]):
            output = model_y[k, :, :]
            if data_m[k] == j:
                output = data_y[k, :, :]
            else:
                output[data_y[k, :, :] == 1] = 0
            model_y[k, :, :] = output

        new_data_y[:, :, :, j] = model_y
    new_data_y[:, :, :, -1] = project_configuration['shared_model_unknown_class_threshold']
    new_data_y = gaussian_filter(new_data_y, sigma=(1.5, 1.5), axes=(1, 2), mode='nearest')
    max_indices = np.argmax(new_data_y, axis=-1)
    one_hot_y = np.zeros_like(new_data_y)
    J, K, L = np.indices(max_indices.shape)
    one_hot_y[J, K, L, max_indices] = 1

    ontologies.append("Unknown")
    for j, o in enumerate(ontologies):
        print(j, o)
        out_tif = np.squeeze(one_hot_y[:, :, :, j]).astype(np.float32)
        tifffile.imwrite(os.path.join(project_configuration["root"], "training_datasets", "phase2", f"out_{o}.tif"), out_tif)
    ontologies.remove("Unknown")

    print(f"Saved phase2 training data. Image sizes:\n\tin:  {data_x.shape}\n\tout: {one_hot_y.shape}")
    print(f"Features:\n\tin:  {project_configuration['macromolecules']}\n\tout:  {project_configuration['ontologies']+['Unknown']}")


def phase_2_train(gpus, checkpoint=''):
    import tensorflow as tf
    import keras.callbacks
    from Pom.models.phase2model import create_model#, dice_loss, combined_loss

    os.makedirs(os.path.join(project_configuration['root'], "models", "phase2"), exist_ok=True)
    os.environ["CUDA_VISIBLE_DEVICES"] = gpus

    if checkpoint != '' and not os.path.isabs(checkpoint):
        checkpoint = os.path.abspath(checkpoint)

    def add_redundancy(data):
        data_out = list()
        for img in data:
            for k in [0, 1, 2, 3]:
                _img = np.rot90(img, k, axes=(0, 1))
                data_out.append(_img)
                data_out.append(np.flip(_img, axis=0))
        return np.array(data_out)

    macromolecule_inputs = project_configuration["macromolecules"]
    ontologies = project_configuration["ontologies"]
    ontologies.append("Unknown")

    data_y = list()
    data_x = list()

    for o in ontologies:
        data_y.append(add_redundancy(tifffile.imread(os.path.join(project_configuration["root"], "training_datasets", "phase2", f"out_{o}.tif"))))
    for m in macromolecule_inputs:
        data_x.append(add_redundancy(tifffile.imread(os.path.join(project_configuration["root"], "training_datasets", "phase2", f"in_{m}.tif"))))

    data_y = np.stack(data_y, axis=-1)
    data_x = np.stack(data_x, axis=-1)

    def tf_data_generator():
        n_samples = data_x.shape[0]
        indices = np.arange(n_samples)

        while True:
            np.random.shuffle(indices)
            for i in range(0, n_samples, project_configuration["shared_model_batch_size"]):
                batch_indices = indices[i:i + project_configuration["shared_model_batch_size"]]
                batch_x = data_x[batch_indices]
                batch_y = data_y[batch_indices]
                yield batch_x, batch_y

    training_data = tf.data.Dataset.from_generator(tf_data_generator, output_signature=(tf.TensorSpec(shape=(None, data_x.shape[1], data_x.shape[2], data_x.shape[3]), dtype=tf.float32), tf.TensorSpec(shape=(None, data_y.shape[1], data_y.shape[2], data_y.shape[3]), dtype=tf.float32)))
    options = tf.data.Options()
    options.experimental_distribute.auto_shard_policy = tf.data.experimental.AutoShardPolicy.DATA
    training_data = training_data.with_options(options)

    strategy = tf.distribute.MirroredStrategy()
    with strategy.scope():
        if checkpoint != '' and os.path.exists(checkpoint):
            model = tf.keras.models.load_model(checkpoint)
        else:
            model = create_model(data_x.shape[1:], output_dimensionality=data_y.shape[-1])

    checkpoint_callback = keras.callbacks.ModelCheckpoint(filepath=os.path.join(project_configuration["root"], "models", "phase2", f"CombinedOntologies_checkpoint.h5"), monitor='loss', mode='min', save_best_only=True)
    model.fit(training_data, epochs=project_configuration["shared_model_epochs"], steps_per_epoch=data_x.shape[0] // project_configuration["shared_model_batch_size"], shuffle=True, callbacks=[checkpoint_callback])
    model.save(os.path.join(project_configuration["root"], "models", "phase2", f"CombinedOntologies.h5"))


def phase_2_process(gpus="0"):
    import tensorflow as tf
    from scipy.ndimage.filters import convolve1d
    from numpy.random import shuffle
    import itertools
    import multiprocessing
    from Pom.models.phase2model import create_model

    os.makedirs(os.path.join(project_configuration["root"], project_configuration['output_dir']), exist_ok=True)

    def preprocess_volume(vol):
        return bin_vol(convolve1d(vol, np.ones(2 * project_configuration["z_sum"] + 1) / (2 * project_configuration["z_sum"] + 1), axis=0, mode='nearest'), 2)

    def segment_tomo(tomo, model, n_features):
        components = dict()

        tomo_name = os.path.splitext(os.path.basename(tomo))[0]
        n_placeholders = 0
        for m in project_configuration["macromolecules"]:
            if m == 'Density':
                components[m] = preprocess_volume(mrcfile.read(os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], f"{tomo_name}.mrc")))
                components[m] -= np.mean(components[m])
                components[m] /= np.std(components[m])
            elif m == '_':
                components[f'_{n_placeholders}'] = None
                n_placeholders += 1
            else:
                components[m] = preprocess_volume(mrcfile.read(os.path.join(project_configuration["root"], project_configuration["macromolecule_dir"], f"{tomo_name}__{m}.mrc"))) / 255.0 * 2.0 - 1.0

        input_component_0 = components[[m for m in list(components.keys()) if "_" not in m][0]]
        for m in components:
            if "_" in m:
                components[m] = np.zeros_like(input_component_0) - 1.0

        data_x = np.zeros((*components[project_configuration["macromolecules"][0]].shape, len(project_configuration["macromolecules"])), dtype=np.float32)
        for j, m in enumerate(components):
            data_x[:, :, :, j] = components[m]

        data_y = np.zeros((*data_x.shape[0:3], n_features), dtype=np.float32)
        out_w = 32 * (data_y.shape[1] // 32)
        out_w_margin = (data_y.shape[1] % 32) // 2
        out_h = 32 * (data_y.shape[2] // 32)
        out_h_margin = (data_y.shape[2] % 32) // 2
        n_runs = max(min(4, project_configuration['shared_model_runs_per_volume']), 1)
        for j in range(data_y.shape[0]):
            slice_j = data_x[j, :, :, :]
            for k in range(n_runs):
                rotated_slice = np.rot90(slice_j, k=k, axes=(0, 1))
                w = 32 * (rotated_slice.shape[0] // 32)
                w_pad = (rotated_slice.shape[0] % 32) // 2
                h = 32 * (rotated_slice.shape[1] // 32)
                h_pad = (rotated_slice.shape[1] % 32) // 2
                data_y[j, out_w_margin:out_w_margin+out_w, out_h_margin:out_h_margin+out_h, :] += np.rot90(np.squeeze(model.predict(rotated_slice[w_pad:w_pad+w, h_pad:h_pad+h][np.newaxis, :, :])), k=-k, axes=(0, 1))
        data_y /= n_runs
        return data_y

    def _thread(model_path, tomogram_paths, gpu_id, ontology_names):
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

        inference_model = create_model((None, None, len(project_configuration["macromolecules"])), output_dimensionality=len(project_configuration["ontologies"]))
        trained_model = tf.keras.models.load_model(model_path, compile=False)
        for nl, l in zip(inference_model.layers, trained_model.layers):
            nl.set_weights(l.get_weights())

        for j, tomo in enumerate(tomogram_paths):
            t_start = time.time()
            try:
                out_name = os.path.join(project_configuration["root"], project_configuration['output_dir'], os.path.basename(os.path.splitext(tomo)[0])+f"__{ontology_names[0]}.mrc")
                if not os.path.exists(out_name):
                    with mrcfile.new(out_name, overwrite=True) as f:
                        f.set_data(-np.ones((10, 10, 10), dtype=np.float32))
                        f.voxel_size = project_configuration["apix"] * 2
                else:
                    print(f"skipping {os.path.splitext(os.path.basename(tomo))[0]} (output already exists in {project_configuration['output_dir']})")
                    continue
                vol_out = segment_tomo(tomo, inference_model, len(ontology_names))
                for k, o in enumerate(ontology_names):
                    if o == "_":
                        continue
                    with mrcfile.new(os.path.join(project_configuration["root"], project_configuration['output_dir'], os.path.basename(os.path.splitext(tomo)[0])+f"__{o}.mrc"), overwrite=True) as f:
                        f.set_data(vol_out[:, :, :, k].astype(np.float32))
                        f.voxel_size = project_configuration["apix"] * 2
                print(f"(GPU {gpu_id}) {j+1}/{len(tomogram_paths)} cost: {time.time() - t_start:.1f} seconds {(time.time() - t_start) / len(ontology_names):.1f} per feature.")
            except Exception as e:
                print(e)

    ontologies = project_configuration["ontologies"]
    all_tomos = glob.glob(os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], "*.mrc"))
    shuffle(all_tomos)
    _gpus = [int(j) for j in gpus.split(",")]
    data_div = {gpu: list() for gpu in _gpus}
    for gpu, tomo_path in zip(itertools.cycle(_gpus), all_tomos):
        data_div[gpu].append(tomo_path)

    ontologies.append("Unknown")
    processes = []
    for gpu_id in data_div:
        p = multiprocessing.Process(target=_thread, args=(os.path.join(project_configuration["root"], "models", "phase2", f"CombinedOntologies.h5"), data_div[gpu_id], gpu_id, ontologies))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()


def phase_3_summarize(overwrite=False, skip_macromolecules=False, target_feature=None):
    import pandas as pd

    data_directories = [project_configuration["output_dir"]]
    if not skip_macromolecules:
        data_directories.append(project_configuration["macromolecule_dir"])

    summary_path = os.path.join(project_configuration["root"], 'summary.xlsx')
    df = pd.DataFrame() if not os.path.exists(summary_path) else pd.read_excel(summary_path, index_col=0)

    files = list()
    for d in data_directories:
        files += glob.glob(os.path.join(project_configuration["root"], d, "*__*.mrc"))

    valid_features = project_configuration["macromolecules"] + project_configuration["ontologies"] + ["Unknown"]

    print(f'Found {len(files)} files to summarize.')

    for i, f in enumerate(files, start=1):
        tag = os.path.basename(f).split("__")[0]
        feature = os.path.splitext(os.path.basename(f))[0].split("__")[-1]
        if feature not in valid_features:
            continue
        if target_feature is not None and feature != target_feature:
            continue
        if not overwrite and tag in df.index and feature in df.columns and not pd.isna(df.at[tag, feature]):
            continue

        print(f"{i}/{len(files)}\t{feature:<30}{os.path.basename(f)}")

        volume = mrcfile.mmap(f).data
        n_slices_margin = int(project_configuration["z_margin_summary"] * volume.shape[0])
        volume = volume[n_slices_margin:-n_slices_margin, :, :]

        if volume[0, 0, 0] == -1:  # then it's a placeholder volume.
            continue

        if volume.dtype == np.float32:
            val = np.sum(volume) * 100.0 / np.prod(volume.shape)
        else:
            val = np.sum(volume) / 255.0 * 100.0 / np.prod(volume.shape)

        df.at[tag, feature] = val

    if "Void" in df.columns:
        df.sort_values(by="Void")

    df.to_excel(summary_path, index=True, index_label="Tomogram")

    print(f"Dataset summary saved at {summary_path}")


def render_volumes(renderer, tomo_path, requested_compositions, feature_library, overwrite=False, save=True, df_summary=None):
    from Pom.core.render import VolumeModel, SurfaceModel
    from PIL import Image

    def get_volume(tomo_path, feature_name):
        tomo_tag = os.path.splitext(os.path.basename(tomo_path))[0]

        # Look for the feature in the macromolecule and output directories
        m_path = glob.glob(os.path.join(project_configuration["root"], project_configuration["macromolecule_dir"], f"{tomo_tag}__{feature_name}.mrc"))
        o_path = glob.glob(os.path.join(project_configuration["root"], project_configuration["output_dir"], f"{tomo_tag}__{feature_name}.mrc"))
        # Try to load the MRC file
        mrc_file = None
        if len(m_path) > 0 and os.path.exists(m_path[0]):
            mrc_file = m_path[0]
        elif len(o_path) > 0 and os.path.exists(o_path[0]):
            mrc_file = o_path[0]

        # If the MRC file is found, read it and get the pixel size
        if mrc_file:
            with mrcfile.open(mrc_file, permissive=True) as mrc:
                volume = np.copy(mrc.data)
                pixel_size = mrc.voxel_size.x  # Get the pixel size (in nanometers by default)

            # Return the volume and pixel size
            return volume, pixel_size

        # If no MRC file is found, raise an exception
        raise Exception(f"Could not find feature {feature_name} for tomogram at {tomo_path}")

    def render_compositions(tomo_path, requested_compositions, feature_library, overwrite=False):
        skip_composition = list()
        if not overwrite:
            image_base_name = os.path.basename(os.path.splitext(tomo_path)[0])
            for composition_name in requested_compositions:
                out_filename = os.path.join(project_configuration["root"], project_configuration["image_dir"], f"{image_base_name}_{composition_name}.png")
                if os.path.exists(out_filename):
                    skip_composition.append(True)
                else:
                    skip_composition.append(False)
            # check if any image already there.

        renderables = dict()
        for j, c in enumerate(requested_compositions.values()):
            if not overwrite and skip_composition[j]:
                continue
            for feature in c:
                if feature not in renderables:
                    try:
                        feature_volume, pixel_size = get_volume(tomo_path, feature)
                        if feature != "Lipid droplet" and (feature in project_configuration["ontologies"] or feature == "Unknown") and project_configuration["raytraced_ontologies"]:
                            renderables[feature] = VolumeModel(feature_volume, feature_library[feature], pixel_size)
                        else:
                            renderables[feature] = SurfaceModel(feature_volume, feature_library[feature], pixel_size)
                    except Exception as e:
                        print(e)

        image_base_name = os.path.basename(os.path.splitext(tomo_path)[0])
        out_images = dict()
        for composition_name in requested_compositions:
            if requested_compositions[composition_name] == []:
                continue
            renderer.new_image()
            renderer.render([renderables[f] for f in requested_compositions[composition_name] if f in renderables])
            image = renderer.get_image()
            if save:
                Image.fromarray(image).save(os.path.join(project_configuration["root"], project_configuration["image_dir"], composition_name, f"{image_base_name}_{composition_name}.png"))
            else:
                out_images[composition_name] = image

        for s in renderables.values():
            s.delete()

    # parse compositions
    tomo_name = os.path.splitext(os.path.basename(tomo_path))[0]
    sorted_ontologies = df_summary.loc[tomo_name].sort_values(ascending=False).index.tolist()
    for f in project_configuration["soft_ignore_in_summary"] + project_configuration["macromolecules"]:
        if f in sorted_ontologies:
            sorted_ontologies.remove(f)
    for f in sorted_ontologies:
        if f not in project_configuration["ontologies"]:
            sorted_ontologies.remove(f)

    tomo_req_compositions = dict()
    for name, composition in zip(requested_compositions.keys(), requested_compositions.values()):
        composition_features = list()
        available_ontologies = copy.deepcopy(sorted_ontologies)
        for feature in composition:
            if feature[0] == "!":
                if feature[1:] in available_ontologies:
                    available_ontologies.remove(feature[1:])

        for feature in composition:
            if "rank" in feature:
                j = int(feature.split("rank")[-1]) - 1
                if j < len(available_ontologies):
                    feature = available_ontologies[j]
                else:
                    continue
            if "!" in feature:
                continue
            composition_features.append(feature)
            if feature not in feature_library:
                print(f"Feature {feature} not in feature library!")
                feature_library[feature] = FeatureLibraryFeature()
                feature_library[feature].title = feature

        tomo_req_compositions[name] = composition_features

    render_compositions(tomo_path, tomo_req_compositions, feature_library, overwrite=overwrite)


def phase_3_render(composition_path="", n=-1, tomo_name='', overwrite=False, parallel_processes="1", feature_library_path=None):
    from Pom.core.render import Renderer
    from numpy.random import shuffle
    import pandas as pd
    import itertools
    import multiprocessing

    os.makedirs(os.path.join(project_configuration["root"], project_configuration["image_dir"]), exist_ok=True)

    if composition_path != "" and not os.path.isabs(composition_path):
        composition_path = os.path.join(os.getcwd(), composition_path)

    m_feature_library = feature_library
    if feature_library_path:
        if not os.path.isabs(feature_library_path):
            feature_library_path = os.path.join(os.getcwd(), feature_library_path)
        m_feature_library = parse_feature_library(feature_library_path)

    #
    df = pd.read_excel(os.path.join(project_configuration["root"], "summary.xlsx"), index_col=0)
    df = df.dropna()
    all_tomograms = [os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], f"{t}.mrc") for t in df.index]

    shuffle(all_tomograms)
    if n > -1:
        all_tomograms = all_tomograms[:min(n, len(all_tomograms))]
    if tomo_name != '':
        glob_pattern = os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], f"*{tomo_name}*.mrc")
        all_tomograms = glob.glob(glob_pattern)
        if len(all_tomograms) == 0:
            print(f"No tomograms found with pattern {glob_pattern}")


    if os.path.exists(composition_path):
        with open(composition_path, 'r') as f:
            requested_compositions = json.load(f)
    else:
        requested_compositions = {"Macromolecules": [m for m in project_configuration["macromolecules"] if m not in ["_", "Density"]],
                                  "Top3": ["rank1", "rank2", "rank3", "!Unknown"]}

    for key in requested_compositions.keys():
        os.makedirs(os.path.join(project_configuration["root"], project_configuration["image_dir"], key), exist_ok=True)

    def _thread(tomo_paths, df_summary, feature_library):
        renderer = Renderer(image_size=project_configuration["image_size"])

        for j, t in enumerate(tomo_paths):
            render_volumes(renderer, t, requested_compositions, feature_library, overwrite, df_summary=df_summary)
            print(f"{j+1}/{len(tomo_paths)} - {t}")
        renderer.delete()

    # df = df.sort_values(by="Void")
    # all_tomograms = [os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], f"{t}.mrc") for t in df.index]
    #
    # df = df.sort_values(by="ATP synthase", ascending=False)
    # df = df[df["Mitochondrion"] >= 10.0]
    # all_tomograms = [os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], f"{t}.mrc") for t in df.index]
    print(f"Preparing to render images for {len(all_tomograms)} tomograms.")
    parallel_processes = int(parallel_processes)
    if parallel_processes == 1:
        _thread(all_tomograms, df, m_feature_library)
    else:
        process_div = {p: list() for p in range(parallel_processes)}
        for p, tomo_path in zip(itertools.cycle(range(parallel_processes)), all_tomograms):
            process_div[p].append(tomo_path)

        processes = []
        for p in process_div:
            processes.append(multiprocessing.Process(target=_thread, args=(process_div[p], df, m_feature_library)))
            processes[-1].start()
        for p in processes:
            p.join()


def phase_3_projections(overwrite=False, parallel_processes=1):
    from PIL import Image
    import multiprocessing
    import itertools
    from scipy.ndimage import gaussian_filter1d

    def compute_autocontrast(img, saturation=0.5):
        subsample = img[::2, ::2]
        n = subsample.shape[0] * subsample.shape[1]
        sorted_pixelvals = np.sort(subsample.flatten())

        min_idx = min([int(saturation / 100.0 * n), n - 1])
        max_idx = max([int((1.0 - saturation / 100.0) * n), 0])
        return sorted_pixelvals[min_idx], sorted_pixelvals[max_idx]

    all_tomograms = list()
    for tomo in glob.glob(os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], "*.mrc")):
        tomo_name = os.path.splitext(os.path.basename(tomo))[0]
        density_out = os.path.join(project_configuration["root"], project_configuration["image_dir"], "density", f"{tomo_name}_density.png")
        if not os.path.exists(density_out) or overwrite:
            all_tomograms.append(tomo_name)


    ontologies = project_configuration["ontologies"]
    if not "Unknown" in ontologies:
        ontologies.append("Unknown")

    os.makedirs(os.path.join(project_configuration["root"], project_configuration["image_dir"], "density"), exist_ok=True)
    for o in ontologies:
        os.makedirs(os.path.join(project_configuration["root"], project_configuration["image_dir"], f"{o}_projection"), exist_ok=True)

    def process_tomogram(tomo):
        out_base = os.path.join(project_configuration["root"], project_configuration["image_dir"])

        images_xy = dict()
        images_xz = dict()
        xy_max = 1
        xz_max = 1
        for o in ontologies:
            path = os.path.join(project_configuration["root"], project_configuration["output_dir"], f"{tomo}__{o}.mrc")
            if not os.path.exists(path):
                continue
            if not overwrite and os.path.exists(os.path.join(out_base, f"{o}_projection", f"{tomo}_{o}.png")):
                continue
            with mrcfile.open(path) as mrc:
                n_slices_margin = int(project_configuration["z_margin_summary"] * mrc.data.shape[0])
                data = copy.copy(mrc.data[n_slices_margin:-n_slices_margin, :, :])
                data = gaussian_filter1d(data, sigma=3.0, axis=0)
            threshold = 0.5
            data_mask = data > threshold
            images_xy[o] = np.sum(data_mask, axis=0)
            images_xz[o] = np.sum(data_mask, axis=1)
            if o == "Void":
                continue
            _max = np.amax(images_xy[o])
            if _max > xy_max:
                xy_max = _max
            _max = np.amax(images_xz[o])
            if _max > xz_max:
                xz_max = _max

        for o in ontologies:
            if not o in images_xy:
                continue

            img_xy = images_xy[o]
            img_xz = images_xz[o]
            if o == "Void":
                img_xy = img_xy / np.amax(img_xy)
                img_xz = img_xz / np.amax(img_xz)
                img_xy *= 255
                img_xz *= 255
            else:
                img_xy = img_xy / xy_max * 255 * 1.50
                img_xz = img_xz / xz_max * 255 * 1.50

            img_xy = np.clip(img_xy, 0, 255)
            img_xz = np.clip(img_xz, 0, 255)
            img_xy = img_xy.astype(np.uint8)
            img_xz = img_xz.astype(np.uint8)
            Image.fromarray(img_xy, mode='L').save(os.path.join(out_base, f"{o}_projection", f"{tomo}_{o}.png"))
            Image.fromarray(img_xz, mode='L').save(os.path.join(out_base, f"{o}_projection", f"{tomo}_{o}_side.png"))

        if not os.path.exists(os.path.join(out_base, "density", f"{tomo}_density.png")) or overwrite:
            with mrcfile.open(os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], f"{tomo}.mrc")) as mrc:
                n_slices = mrc.data.shape[0]
                density = copy.copy(mrc.data[n_slices//2, :, :])
                contrast_lims = compute_autocontrast(density)
                density -= contrast_lims[0]
                density /= (contrast_lims[1] - contrast_lims[0])
                density = np.clip(density * 255, 0, 255).astype(np.uint8)
                Image.fromarray(density, mode='L').save(os.path.join(out_base, "density", f"{tomo}_density.png"))

    def _thread(tomo_list):
        for j, t in enumerate(tomo_list):
            print(f"{j+1}/{len(tomo_list)} {os.path.splitext(os.path.basename(t))[0]}")
            process_tomogram(t)

    parallel_processes = int(parallel_processes)
    if parallel_processes == 1:
        _thread(all_tomograms)
    else:
        process_div = {p: list() for p in range(parallel_processes)}
        for p, tomo_path in zip(itertools.cycle(range(parallel_processes)), all_tomograms):
            process_div[p].append(tomo_path)

        processes = []
        for p in process_div:
            processes.append(multiprocessing.Process(target=_thread, args=(process_div[p], )))
            processes[-1].start()
        for p in processes:
            p.join()


def phase_3_browse():
    app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'Introduction.py')
    print(f'streamlit run "{app_path}"')
    os.system(f'streamlit run "{app_path}"')


def phase_3_capp(config_file_path, context_window_size, bin_factor, parallel):
    import multiprocessing
    import itertools
    from copy import copy

    if not os.path.isabs(config_file_path) and not os.path.exists(config_file_path):
        config_file_path = os.path.abspath(os.path.join(project_configuration["root"], "capp", f"{config_file_path}", "config.json"))

    job_dir = os.path.dirname(config_file_path)
    with open(config_file_path, 'r') as f:
        job_config = json.load(f)
        target = job_config["target"]
        context_elements = job_config["context_elements"]

    def _capp_job(tomo, job_dir, target, context_window_size, bin_factor, context_elements):

        coordinate_path = os.path.join(job_dir, "coordinates", f"{tomo}__{target}_coords.star")
        df = starfile.read(coordinate_path)

        coordinates = list(
            zip(
                df['rlnCoordinateX'].astype(int),
                df['rlnCoordinateY'].astype(int),
                df['rlnCoordinateZ'].astype(int)
            )
        )
        out_lines = list()
        out_header = "X\tY\tZ"
        context_volumes = dict()
        for f in context_elements:
            out_header += f"\t{f}"
            context_volume_path = os.path.join(project_configuration["root"], project_configuration["output_dir"], f"{tomo}__{f}.mrc")
            if os.path.exists(context_volume_path):
                context_volumes[f] = mrcfile.mmap(context_volume_path).data
            else:
                context_volumes[f] = None
                print(f"Context volume {context_volume_path} does not exists - writing context value of 0 as placeholder.")
        out_header += "\n"

        w = context_window_size // 2 // bin_factor
        for c in coordinates:
            l, k, j = c
            if l < context_window_size // 2 or k < context_window_size // 2 or j < context_window_size // 2:
                continue
            out_lines.append(f"{l}\t{k}\t{j}")

            l //= bin_factor
            k //= bin_factor
            j //= bin_factor

            for f in context_volumes:
                if context_volumes[f] is None:
                    v_context = 0.0
                else:
                    v_context = copy(context_volumes[f][j-w:j+w+1, k-w:k+w+1, l-w:l+w+1])
                    v_context = np.mean(v_context)
                out_lines[-1] += f"\t{v_context:.3f}"

            out_lines[-1] += "\n"

        with open(os.path.join(job_dir, f"{tomo}__{target}_coords.tsv"), 'w') as f:
            f.write(out_header)
            f.writelines(out_lines)

    def _capp_thread(tomos, thread_id, job_dir, target, context_window_size, bin_factor, context_elements):
        for j, p in enumerate(tomos):
            _capp_job(p, job_dir, target, context_window_size, bin_factor, context_elements)
            print(f"{j+1}/{len(tomos)} (thread {thread_id}) - {p}")

    tomos = [os.path.basename(f).split('__')[0] for f in glob.glob(os.path.join(job_dir, "coordinates", "*.star"))]
    print(f"Found {len(tomos)} coordinate files in {os.path.join(job_dir, 'coordinates')}")
    if len(tomos) == 0:
        return
    
    parallel_processes = int(parallel)
    if parallel_processes == 1:
        _capp_thread(tomos, 0, job_dir=job_dir, target=target, context_window_size=context_window_size, bin_factor=bin_factor, context_elements=context_elements)
    else:
        process_div = {p: list() for p in range(parallel)}
        for p, tomo in zip(itertools.cycle(range(parallel)), tomos):
            process_div[p].append(tomo)
        processes = list()
        for p in process_div:
            processes.append(multiprocessing.Process(target=_capp_thread, args=(process_div[p], p, job_dir, target, context_window_size, bin_factor, context_elements)))
            processes[-1].start()
        for p in processes:
            p.join()

    capp_files = glob.glob(os.path.join(job_dir, "*.tsv"))
    combined_lines = list()
    for cf in capp_files:
        if os.path.basename(cf) == 'all_particles.tsv':
            continue
        tomo_name = os.path.basename(cf).split("__")[0]
        with open(cf, 'r') as f:
            lines = f.readlines()
            for l in lines[1:]:
                combined_lines.append(f"{l.rstrip()}\t{tomo_name}\n")

    with open(cf, 'r') as f:
        header = f.readline().rstrip()
        header += "\ttomo\n"

    with open(os.path.join(job_dir, "all_particles.tsv"), 'w') as f:
        f.write(header)
        for l in combined_lines:
            f.write(l)


def phase_3_astm_run(config_file_path, overwrite, save_indices=False, save_masks=False, tomo=None):
    import Pommie
    Pommie.compute.initialize()

    if not os.path.isabs(config_file_path) and not os.path.exists(config_file_path):
        config_file_path = os.path.abspath(os.path.join(project_configuration["root"], "astm", f"{config_file_path}", "config.json"))

    def generate_volume_mask(tomo, job_config):
        selection_criteria = job_config["selection_criteria"]

        masks = list()
        for rule in selection_criteria:
            feature_path = os.path.join(project_configuration["root"], project_configuration["output_dir"], f"{tomo}__{rule['feature']}.mrc")
            vol = Pommie.typedefs.Volume.from_path(feature_path)
            if rule["edge"]:
                vol = vol.to_shell_mask(rule["threshold"], int(10 * rule["edge_out"] / vol.apix), int(10 * rule["edge_in"] / vol.apix))
            else:
                vol = vol.threshold(rule["threshold"])

            masks.append(vol)

        out_mask = np.zeros_like(masks[-1].data)
        for m, rule in zip(masks, selection_criteria):
            if rule["logic"] == "include":
                out_mask = np.logical_or(out_mask, m.data)
        for m, rule in zip(masks, selection_criteria):
            if rule["logic"] == "exclude":
                out_mask = np.logical_and(out_mask, np.logical_not(m.data))

        out_mask = Pommie.typedefs.Volume.from_array(out_mask, apix=masks[-1].apix)

        if job_config["template_binning"] == 1:
            out_mask = out_mask.unbin(2)
        else:
            out_mask = out_mask.bin(int(job_config["template_binning"] / 2))

        return out_mask

    job_dir = os.path.dirname(config_file_path)
    with open(config_file_path, 'r') as f:
        job_config = json.load(f)

    polar_min_rad = (job_config["transform_polar_min"]) * np.pi / 180.0
    polar_max_rad = (job_config["transform_polar_max"]) * np.pi / 180.0
    transforms = Pommie.typedefs.Transform.sample_unit_sphere(n_samples=job_config["transform_n"],
                                                              polar_lims=(polar_min_rad, polar_max_rad))

    template = Pommie.typedefs.Particle.from_path(job_config["template_path"])
    template = template.bin(job_config["template_binning"])
    if job_config["template_blur"] > 0:
        template = Pommie.compute.gaussian_filter([template], sigma=job_config["template_blur"])[0]

    template_mask = Pommie.typedefs.Particle.from_path(job_config["template_mask_path"])
    template_mask = template_mask.bin(job_config["template_binning"])

    spherical_mask = Pommie.typedefs.Mask(template)
    spherical_mask.spherical(radius_px=spherical_mask.n // 2)
    template.data *= spherical_mask.data
    template_mask.data *= spherical_mask.data

    Pommie.compute.set_tm2d_n(n=template.n)

    if tomo is not None:
        tomos = [os.path.splitext(tomo)[0]]
    else:
        tomos = [os.path.basename(os.path.splitext(f)[0]) for f in glob.glob(os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], f"*.mrc"))]
    skip_binding = False

    for j, t in enumerate(tomos):
        try:
            out_path = os.path.join(job_dir, f"{t}__score.mrc")
            t_start = time.time()
            if os.path.exists(out_path) and not overwrite:
                print(f"{j+1}/{len(tomos)} - skipping {t} as output exists.")
                continue
            else:
                with mrcfile.new(out_path, overwrite=True) as f:
                    f.set_data(np.zeros((10, 10, 10), dtype=np.float32) - 1)

            volume_mask = generate_volume_mask(t, job_config)  # binning volume_mask is handled inside here
            volume = Pommie.typedefs.Volume.from_path(os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], f"{t}.mrc"))
            volume.bin(job_config["template_binning"])

            scores, indices = Pommie.compute.find_template_in_volume(volume=volume,
                                                                     volume_mask=volume_mask,
                                                                     template=template,
                                                                     template_mask=template_mask,
                                                                     transforms=transforms,
                                                                     dimensionality=2,
                                                                     stride=job_config["stride"],
                                                                     skip_binding=skip_binding,
                                                                     verbose=False)
            skip_binding = True  # only need to bind once; first compute.find_template_in_volume call will do it.
            print(f"{j + 1}/{len(tomos)} ({time.time() - t_start:.2f} seconds)- {t}")
            with mrcfile.new(out_path, overwrite=True) as f:
                f.set_data(scores)
                f.voxel_size = volume.apix
            if save_indices:
                with mrcfile.new(out_path.split("__")[0]+"__indices.mrc", overwrite=True) as f:
                    f.set_data(indices)
                    f.voxel_size = volume.apix
            if save_masks:
                with mrcfile.new(out_path.split("__")[0]+"__mask.mrc", overwrite=True) as f:
                    f.set_data(volume_mask.data.astype(np.float32))
                    f.voxel_size = volume_mask.apix
        except Exception as e:
            print(f"{j+1}/{len(tomos)} - skipping {t} due to error.")
            print(e)
            print()


def phase_3_astm_pick(config_file_path, threshold, spacing, spacing_px=None, parallel=1, max_particles_per_tomogram=1e9, blur_kernel_px=0):
    from Ais.core.util import peak_local_max
    import itertools
    import multiprocessing
    from scipy.ndimage import gaussian_filter

    if not os.path.isabs(config_file_path) and not os.path.exists(config_file_path):
        config_file_path = os.path.abspath(os.path.join(project_configuration["root"], "astm", f"{config_file_path}", "config.json"))

    data_directory = os.path.dirname(config_file_path)
    output_directory = os.path.join(data_directory, "coordinates")
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)
    os.makedirs(output_directory, exist_ok=True)
    all_data_paths = list(filter(lambda f: os.path.getsize(f) > 10000, glob.glob(os.path.join(data_directory, "*__score.mrc"))))

    def _picking_thread(data_paths, output_directory, threshold, spacing, spacing_px=None, thread_id=0, max_per_tomogram=1e9, blur_kernel_px=0):
        for j, p in enumerate(data_paths):
            out_path = os.path.join(output_directory, os.path.basename(os.path.splitext(p)[0])+"_coords.tsv")

            with mrcfile.open(p) as f:
                vol = f.data
                pxs = f.voxel_size

            if blur_kernel_px > 0:
                vol = gaussian_filter(vol, sigma=blur_kernel_px)

            min_distance = int((spacing / pxs)) if spacing_px is None else spacing_px
            coordinates = peak_local_max(vol, min_distance=min_distance, threshold_abs=threshold)
            n_picked = 0
            with open(out_path, 'w') as f:
                for c in coordinates:
                    n_picked += 1
                    coord_score = vol[c[0], c[1], c[2]]
                    f.write(f"{c[0]}\t{c[1]}\t{c[2]}\t{coord_score}\n")
                    if n_picked >= max_per_tomogram:
                        break
            print(f"{j+1}/{len(data_paths)} (thread {thread_id}) - {n_picked} particles in {out_path}")

    data_div = {p_id: list() for p_id in range(parallel)}
    for p_id, p in zip(itertools.cycle(range(parallel)), all_data_paths):
        data_div[p_id].append(p)

    if parallel == 1:
        _picking_thread(all_data_paths, output_directory, threshold, spacing, spacing_px, 1, max_particles_per_tomogram, blur_kernel_px)
    else:
        processes = []
        for p_id in data_div:
            p = multiprocessing.Process(target=_picking_thread,
                                        args=(data_div[p_id], output_directory, threshold, spacing, spacing_px, p_id, max_particles_per_tomogram, blur_kernel_px))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

    # parse everything to a big overview file with columns:     x   y   z   score   index   tomo
    coordinate_files = glob.glob(os.path.join(data_directory, "coordinates", "*.tsv"))
    particles = list()

    class Particle:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.z = 0
            self.score = 0
            self.tomo = 0
            self.t_idx = 0

        def __str__(self):
            return f"{self.x}\t{self.y}\t{self.z}\t{self.score}\t{self.tomo}\t{self.t_idx}\n"

    for j, cf in enumerate(coordinate_files):
        print(f"{j+1}/{len(coordinate_files)} parsing - {cf}")
        tomo_name = os.path.splitext(os.path.basename(cf))[0].split("__")[0]
        idx_mmap = mrcfile.mmap(os.path.join(data_directory, f"{tomo_name}__indices.mrc"))
        with open(cf, 'r') as f:
            lines = f.readlines()
        for l in lines:
            vals = l.split("\n")[0].split("\t")
            p = Particle()
            p.z = int(vals[0])
            p.y = int(vals[1])
            p.x = int(vals[2])
            p.score = float(vals[3])
            p.t_idx = idx_mmap.data[p.z, p.y, p.x]
            p.tomo = tomo_name
            particles.append(p)

    with open(os.path.join(data_directory, "all_particles.tsv"), 'w') as f:
        for p in particles:
            f.write(f"{p}")


def phase_3_parse_warp(warp_tiltseries_directory='warp_tiltseries'):
    import pandas as pd,xml.etree.ElementTree as ET

    def collapse_xml(_, key, value):
        if key == 'Param':
            return value['@Name'], value['@Value']
        return key, value


    summary_path = os.path.join(project_configuration["root"], 'summary.xlsx')
    df = None if not os.path.exists(summary_path) else pd.read_excel(summary_path, index_col=0)

    if not os.path.exists(warp_tiltseries_directory):
        print(f"Warp tiltseries directory '{warp_tiltseries_directory}' does not exist. Exiting.")
        return

    all_tomos = ['_'.join(os.path.basename(os.path.splitext(f)[0]).split('_')[:-1]) for f in glob.glob(os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], "*.mrc"))]
    warp_suffix = os.path.splitext(glob.glob(os.path.join(project_configuration["root"], project_configuration["tomogram_dir"], "*.mrc"))[0])[0].split('_')[-1]

    for j, tomo in enumerate(all_tomos, start=1):
        tomo_xml = os.path.join(warp_tiltseries_directory, f"{tomo}.xml")
        print(f"{j}/{len(all_tomos)} - {tomo_xml}")

        warp_data = ET.parse(tomo_xml).getroot()

        ctf = {p.get('Name'): p.get('Value') for p in warp_data.find('.//CTF').findall('Param')}

        ctf_resolution_estimate = float(warp_data.get('CTFResolutionEstimate'))
        ctf_defocus = ctf['Defocus']
        # now write to df; but mind that warp names the tomogram something_10.00Apx and the tomostar something.tomostar. annoying.
        df.at[f"{tomo}_{warp_suffix}", 'CTFDefocus'] = ctf_defocus
        df.at[f"{tomo}_{warp_suffix}", 'CTFResolutionEstimate'] = ctf_resolution_estimate


    df.to_excel(summary_path, index=True, index_label="Tomogram")