import numpy as np
import pytest

from semantic_world.connections import PrismaticConnection, RevoluteConnection, Connection6DoF
from semantic_world.exceptions import AddingAnExistingViewError, DuplicateViewError, ViewNotFoundError
from semantic_world.prefixed_name import PrefixedName
from semantic_world.spatial_types.derivatives import Derivatives
from semantic_world.spatial_types.math import rotation_matrix_from_rpy
from semantic_world.spatial_types.spatial_types import TransformationMatrix
from semantic_world.spatial_types.symbol_manager import symbol_manager
from semantic_world.testing import world_setup, pr2_world
from semantic_world.world_entity import View


def test_set_state(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    c1: PrismaticConnection = world.get_connection(l1, l2)
    c1.position = 1.0
    assert c1.position == 1.0
    c2: RevoluteConnection = world.get_connection(r1, r2)
    c2.position = 1337
    assert c2.position == 1337
    c3: Connection6DoF = world.get_connection(world.root, bf)
    transform = rotation_matrix_from_rpy(1, 0, 0)
    transform[0, 3] = 69
    c3.origin = transform
    assert np.allclose(world.compute_forward_kinematics_np(world.root, bf), transform)

    world.set_positions_1DOF_connection({c1: 2})
    assert c1.position == 2.0

    transform[0, 3] += c1.position
    assert np.allclose(l2.global_pose, transform)


def test_construction(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    world.validate()
    assert len(world.connections) == 5
    assert len(world.bodies) == 6
    assert world.state.positions[0] == 0
    assert world.get_connection(l1, l2).dof.name == world.get_connection(r1, r2).dof.name


def test_chain_of_bodies(world_setup):
    world, _, l2, _, _, _ = world_setup
    result = world.compute_chain_of_bodies(root=world.root, tip=l2)
    result = [x.name for x in result]
    assert result == [PrefixedName(name='root', prefix='world'), PrefixedName(name='bf', prefix=None),
                      PrefixedName(name='l1', prefix=None), PrefixedName(name='l2', prefix=None)]


def test_chain_of_connections(world_setup):
    world, _, l2, _, _, _ = world_setup
    result = world.compute_chain_of_connections(root=world.root, tip=l2)
    result = [x.name for x in result]
    assert result == [PrefixedName(name='root_T_bf', prefix=None), PrefixedName(name='bf_T_l1', prefix=None),
                      PrefixedName(name='l1_T_l2', prefix=None)]


def test_split_chain_of_bodies(world_setup):
    world, _, l2, _, _, r2 = world_setup
    result = world.compute_split_chain_of_bodies(root=r2, tip=l2)
    result = tuple([x.name for x in y] for y in result)
    assert result == ([PrefixedName(name='r2', prefix=None), PrefixedName(name='r1', prefix=None)],
                      [PrefixedName(name='bf', prefix=None)],
                      [PrefixedName(name='l1', prefix=None), PrefixedName(name='l2', prefix=None)])


def test_split_chain_of_bodies_adjacent1(world_setup):
    world, _, _, _, r1, r2 = world_setup
    result = world.compute_split_chain_of_bodies(root=r2, tip=r1)
    result = tuple([x.name for x in y] for y in result)
    assert result == ([PrefixedName(name='r2', prefix=None)], [PrefixedName(name='r1', prefix=None)], [])


def test_split_chain_of_bodies_adjacent2(world_setup):
    world, _, _, _, r1, r2 = world_setup
    result = world.compute_split_chain_of_bodies(root=r1, tip=r2)
    result = tuple([x.name for x in y] for y in result)
    assert result == ([], [PrefixedName(name='r1', prefix=None)], [PrefixedName(name='r2', prefix=None)])


def test_split_chain_of_bodies_identical(world_setup):
    world, _, _, _, r1, _ = world_setup
    result = world.compute_split_chain_of_bodies(root=r1, tip=r1)
    result = tuple([x.name for x in y] for y in result)
    assert result == ([], [PrefixedName(name='r1', prefix=None)], [])


def test_split_chain_of_connections(world_setup):
    world, _, l2, _, _, r2 = world_setup
    result = world.compute_split_chain_of_connections(root=r2, tip=l2)
    result = tuple([x.name for x in y] for y in result)
    assert result == ([PrefixedName(name='r1_T_r2', prefix=None), PrefixedName(name='bf_T_r1', prefix=None)],
                      [PrefixedName(name='bf_T_l1', prefix=None), PrefixedName(name='l1_T_l2', prefix=None)])


def test_split_chain_of_connections_adjacent1(world_setup):
    world, _, _, _, r1, r2 = world_setup
    result = world.compute_split_chain_of_connections(root=r2, tip=r1)
    result = tuple([x.name for x in y] for y in result)
    assert result == ([PrefixedName(name='r1_T_r2', prefix=None)], [])


def test_split_chain_of_connections_adjacent2(world_setup):
    world, _, _, _, r1, r2 = world_setup
    result = world.compute_split_chain_of_connections(root=r1, tip=r2)
    result = tuple([x.name for x in y] for y in result)
    assert result == ([], [PrefixedName(name='r1_T_r2', prefix=None)])


def test_split_chain_of_connections_identical(world_setup):
    world, _, _, _, r1, _ = world_setup
    result = world.compute_split_chain_of_connections(root=r1, tip=r1)
    result = tuple([x.name for x in y] for y in result)
    assert result == ([], [])


def test_compute_fk_connection6dof(world_setup):
    world, _, _, bf, _, _ = world_setup
    fk = world.compute_forward_kinematics_np(world.root, bf)
    np.testing.assert_array_equal(fk, np.eye(4))

    connection: Connection6DoF = world.get_connection(world.root, bf)

    world.state[connection.x.name].position = 1.
    world.state[connection.qw.name].position = 0
    world.state[connection.qz.name].position = 1
    world.notify_state_change()
    fk = world.compute_forward_kinematics_np(world.root, bf)
    np.testing.assert_array_equal(fk, [[-1., 0., 0., 1.], [0., -1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]])


def test_compute_fk(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    fk = world.compute_forward_kinematics_np(l2, r2)
    np.testing.assert_array_equal(fk, np.eye(4))

    connection: PrismaticConnection = world.get_connection(r1, r2)

    world.state[connection.dof.name].position = 1.
    world.notify_state_change()
    fk = world.compute_forward_kinematics_np(l2, r2)
    assert np.allclose(fk, np.array([[0.540302, -0.841471, 0., -1.],
                                     [0.841471, 0.540302, 0., 0.],
                                     [0., 0., 1., 0.],
                                     [0., 0., 0., 1.]]))


def test_compute_ik(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    target = np.array([[0.540302, -0.841471, 0., -1.],
                       [0.841471, 0.540302, 0., 0.],
                       [0., 0., 1., 0.],
                       [0., 0., 0., 1.]])
    joint_state = world.compute_inverse_kinematics(l2, r2, target)
    for joint, state in joint_state.items():
        world.state[joint.name].position = state
    world.notify_state_change()
    assert np.allclose(world.compute_forward_kinematics_np(l2, r2), target, atol=1e-3)


def test_compute_fk_expression(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    connection: PrismaticConnection = world.get_connection(r1, r2)
    world.state[connection.dof.name].position = 1.
    world.notify_state_change()
    fk = world.compute_forward_kinematics_np(r2, l2)
    fk_expr = world.compose_forward_kinematics_expression(r2, l2)
    fk_expr_compiled = fk_expr.compile()
    fk2 = fk_expr_compiled.fast_call(*symbol_manager.resolve_symbols(fk_expr_compiled.symbol_parameters))
    np.testing.assert_array_almost_equal(fk, fk2)


def test_apply_control_commands(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    connection: PrismaticConnection = world.get_connection(r1, r2)
    cmd = np.array([100., 0, 0, 0, 0, 0, 0, 0])
    dt = 0.1
    world.apply_control_commands(cmd, dt, Derivatives.jerk)
    assert world.state[connection.dof.name].jerk == 100.
    assert world.state[connection.dof.name].acceleration == 100. * dt
    assert world.state[connection.dof.name].velocity == 100. * dt * dt
    assert world.state[connection.dof.name].position == 100. * dt * dt * dt


def test_compute_relative_pose(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    connection: PrismaticConnection = world.get_connection(l1, l2)
    world.state[connection.dof.name].position = 1.
    world.notify_state_change()

    pose = TransformationMatrix(reference_frame=l2)
    relative_pose = world.transform(pose, l1)
    expected_pose = TransformationMatrix([[1., 0, 0., 1.],
                                          [0., 1., 0., 0.],
                                          [0., 0., 1., 0.],
                                          [0., 0., 0., 1.]])

    np.testing.assert_array_almost_equal(relative_pose.to_np(), expected_pose.to_np())


def test_compute_relative_pose_both(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    world.get_connection(world.root, bf).origin = np.array([[0., -1., 0., 1.],
                                                            [1., 0., 0., 0.],
                                                            [0., 0., 1., 0.],
                                                            [0., 0., 0., 1.]])
    world.notify_state_change()

    pose = TransformationMatrix.from_xyz_rpy(x=1.0, reference_frame=bf)
    relative_pose = world.transform(pose, world.root)
    # Rotation is 90 degrees around z-axis, translation is 1 along x-axis
    expected_pose = np.array([[0., -1., 0., 1.],
                              [1., 0., 0., 1.],
                              [0., 0., 1., 0.],
                              [0., 0., 0., 1.]])

    np.testing.assert_array_almost_equal(relative_pose.to_np(), expected_pose)


def test_compute_relative_pose_only_translation(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    connection: PrismaticConnection = world.get_connection(l1, l2)
    world.state[connection.dof.name].position = 1.
    world.notify_state_change()

    pose = TransformationMatrix.from_xyz_rpy(x=2.0, reference_frame=l2)
    relative_pose = world.transform(pose, l1)
    expected_pose = np.array([[1., 0, 0., 3.],
                              [0., 1., 0., 0.],
                              [0., 0., 1., 0.],
                              [0., 0., 0., 1.]])

    np.testing.assert_array_almost_equal(relative_pose.to_np(), expected_pose)


def test_compute_relative_pose_only_rotation(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    connection: RevoluteConnection = world.get_connection(r1, r2)
    world.state[connection.dof.name].position = np.pi / 2  # 90 degrees
    world.notify_state_change()

    pose = TransformationMatrix(reference_frame=r2)
    relative_pose = world.transform(pose, r1)
    expected_pose = np.array([[0., -1., 0., 0.],
                              [1., 0., 0., 0.],
                              [0., 0., 1., 0.],
                              [0., 0., 0., 1.]])

    np.testing.assert_array_almost_equal(relative_pose.to_np(), expected_pose)


def test_add_view(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    v = View(name=PrefixedName('muh'))
    world.add_view(v)
    with pytest.raises(AddingAnExistingViewError):
        world.add_view(v)
    assert world.get_view_by_name(v.name) == v


def test_duplicate_view(world_setup):
    world, l1, l2, bf, r1, r2 = world_setup
    v = View(name=PrefixedName('muh'))
    world.add_view(v)
    world.views.append(v)
    with pytest.raises(DuplicateViewError):
        world.get_view_by_name(v.name)


def test_merge_world(world_setup, pr2_world):
    world, l1, l2, bf, r1, r2 = world_setup

    base_link = pr2_world.get_body_by_name("base_link")
    r_gripper_tool_frame = pr2_world.get_body_by_name('r_gripper_tool_frame')
    torso_lift_link = pr2_world.get_body_by_name("torso_lift_link")
    r_shoulder_pan_joint = pr2_world.get_connection(torso_lift_link, pr2_world.get_body_by_name("r_shoulder_pan_link"))

    l_shoulder_pan_joint = pr2_world.get_connection(torso_lift_link, pr2_world.get_body_by_name("l_shoulder_pan_link"))

    world.merge_world(pr2_world)

    assert base_link in world.bodies
    assert r_gripper_tool_frame in world.bodies
    assert l_shoulder_pan_joint in world.connections
    assert torso_lift_link._world == world
    assert r_shoulder_pan_joint._world == world


def test_merge_with_connection(world_setup, pr2_world):
    world, l1, l2, bf, r1, r2 = world_setup

    base_link = pr2_world.get_body_by_name("base_link")
    r_gripper_tool_frame = pr2_world.get_body_by_name('r_gripper_tool_frame')
    torso_lift_link = pr2_world.get_body_by_name("torso_lift_link")
    r_shoulder_pan_joint = pr2_world.get_connection(torso_lift_link, pr2_world.get_body_by_name("r_shoulder_pan_link"))

    new_connection = Connection6DoF(parent=l1, child=pr2_world.root, _world=world)

    world.merge_world(pr2_world, new_connection)

    assert base_link in world.bodies
    assert r_gripper_tool_frame in world.bodies
    assert new_connection in world.connections
    assert torso_lift_link._world == world
    assert r_shoulder_pan_joint._world == world


def test_merge_with_pose(world_setup, pr2_world):
    world, l1, l2, bf, r1, r2 = world_setup

    base_link = pr2_world.get_body_by_name("base_link")
    r_gripper_tool_frame = pr2_world.get_body_by_name('r_gripper_tool_frame')
    torso_lift_link = pr2_world.get_body_by_name("torso_lift_link")
    r_shoulder_pan_joint = pr2_world.get_connection(torso_lift_link, pr2_world.get_body_by_name("r_shoulder_pan_link"))

    pose = np.eye(4)
    pose[0, 3] = 1.0  # Translate along x-axis

    world.merge_world_at_pose(pr2_world, pose)

    assert base_link in world.bodies
    assert r_gripper_tool_frame in world.bodies
    assert torso_lift_link._world == world
    assert r_shoulder_pan_joint._world == world
    assert world.compute_forward_kinematics_np(world.root, base_link)[0, 3] == pytest.approx(1.0, abs=1e-6)


def test_merge_with_pose_rotation(world_setup, pr2_world):
    world, l1, l2, bf, r1, r2 = world_setup

    base_link = pr2_world.get_body_by_name("base_link")
    r_gripper_tool_frame = pr2_world.get_body_by_name('r_gripper_tool_frame')
    torso_lift_link = pr2_world.get_body_by_name("torso_lift_link")
    r_shoulder_pan_joint = pr2_world.get_connection(torso_lift_link, pr2_world.get_body_by_name("r_shoulder_pan_link"))
    base_footprint = pr2_world.get_body_by_name("base_footprint")

    # Rotation is 90 degrees around z-axis, translation is 1 along x-axis
    pose = np.array([[0., -1., 0., 1.],
                     [1., 0., 0., 1.],
                     [0., 0., 1., 0.],
                     [0., 0., 0., 1.]])

    world.merge_world_at_pose(pr2_world, pose)

    assert base_link in world.bodies
    assert r_gripper_tool_frame in world.bodies
    assert torso_lift_link._world == world
    assert r_shoulder_pan_joint._world == world
    fk_base = world.compute_forward_kinematics_np(world.root, base_footprint)
    assert fk_base[0, 3] == pytest.approx(1.0, abs=1e-6)
    assert fk_base[1, 3] == pytest.approx(1.0, abs=1e-6)
    assert fk_base[2, 3] == pytest.approx(0.0, abs=1e-6)
    np.testing.assert_array_almost_equal(rotation_matrix_from_rpy(0, 0, np.pi / 2)[:3, :3], fk_base[:3, :3], decimal=6)
