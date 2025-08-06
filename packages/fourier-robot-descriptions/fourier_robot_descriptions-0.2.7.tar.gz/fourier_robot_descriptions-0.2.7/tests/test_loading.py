import pinocchio as pin


def test_loading_time_yourdfpy(benchmark):
    from fourier_robot_descriptions.loaders.yourdfpy import load_robot_description

    benchmark(load_robot_description, ("gr1t1", "fourier_left_hand_6dof", "fourier_right_hand_6dof"))


def test_loading_time_pinocchio(benchmark):
    from fourier_robot_descriptions.loaders.pinocchio import load_robot_description

    benchmark(load_robot_description, ("gr1t1", "fourier_left_hand_6dof", "fourier_right_hand_6dof"))


def test_loading_time_pinocchio_mimic(benchmark):
    from fourier_robot_descriptions.loaders.pinocchio import load_robot_description

    benchmark(
        load_robot_description,
        ("gr1t1", "fourier_left_hand_6dof", "fourier_right_hand_6dof"),
        mimic=True,
    )
