from __future__ import annotations

import inspect
from abc import abstractmethod
from collections import deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, fields
from functools import reduce
from typing import List, Optional, TYPE_CHECKING, Set, get_args, get_type_hints, Deque
import numpy as np
from numpy import ndarray
from typing_extensions import Self

from .geometry import Shape, BoundingBox, BoundingBoxCollection
from dataclasses import dataclass, field
from dataclasses import fields
from functools import lru_cache
from functools import reduce
from typing import List, Optional, TYPE_CHECKING, Tuple
from typing import Set

import numpy as np
from numpy import ndarray
from scipy.stats import geom
from trimesh.proximity import closest_point, nearby_faces
from trimesh.sample import sample_surface

from .geometry import BoundingBox, BoundingBoxCollection
from .geometry import Shape
from .prefixed_name import PrefixedName
from .spatial_types import spatial_types as cas
from .spatial_types.spatial_types import Point3
from .spatial_types.spatial_types import TransformationMatrix, Expression
from .types import NpMatrix4x4
from .utils import IDGenerator

if TYPE_CHECKING:
    from .world import World

id_generator = IDGenerator()


@dataclass(unsafe_hash=True)
class WorldEntity:
    """
    A class representing an entity in the world.
    """

    _world: Optional[World] = field(default=None, repr=False, kw_only=True, hash=False)
    """
    The backreference to the world this entity belongs to.
    """

    _views: Set[View] = field(default_factory=set, init=False, repr=False, hash=False)
    """
    The views this entity is part of.
    """

    name: PrefixedName = field(default=None, kw_only=True)
    """
    The identifier for this world entity.
    """

    def __post_init__(self):
        if self.name is None:
            self.name = PrefixedName(f"{self.__class__.__name__}_{hash(self)}")


@dataclass
class Body(WorldEntity):
    """
    Represents a body in the world.
    A body is a semantic atom, meaning that it cannot be decomposed into meaningful smaller parts.
    """

    visual: List[Shape] = field(default_factory=list, repr=False)
    """
    List of shapes that represent the visual appearance of the link.
    The poses of the shapes are relative to the link.
    """

    collision: List[Shape] = field(default_factory=list, repr=False)
    """
    List of shapes that represent the collision geometry of the link.
    The poses of the shapes are relative to the link.
    """

    index: Optional[int] = field(default=None, init=False)
    """
    The index of the entity in `_world.kinematic_structure`.
    """

    def __post_init__(self):
        if not self.name:
            self.name = PrefixedName(f"body_{id_generator(self)}")

        if self._world is not None:
            self.index = self._world.kinematic_structure.add_node(self)

        for c in self.collision:
            c.origin.reference_frame = self
        for v in self.visual:
            v.origin.reference_frame = self

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name and self._world is other._world

    def has_collision(self) -> bool:
        return len(self.collision) > 0

    def compute_closest_points_multi(self, others: list[Body], sample_size=25) -> Tuple[
        np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes the closest points to each given body respectively.

        :param others: The list of bodies to compute the closest points to.
        :param sample_size: The number of samples to take from the surface of the other bodies.
        :return: A tuple containing: The points on the self body, the points on the other bodies, and the distances. All points are in the of this body.
        """

        @lru_cache(maxsize=None)
        def evaluated_geometric_distribution(n: int) -> np.ndarray:
            """
            Evaluates the geometric distribution for a given number of samples.
            :param n: The number of samples to evaluate.
            :return: An array of probabilities for each sample.
            """
            return geom.pmf(np.arange(1, n + 1), 0.5)

        query_points = []
        for other in others:
            # Calculate the closest vertex on this body to the other body
            closest_vert_id = \
                self.collision[0].mesh.kdtree.query(
                    (self._world.compute_forward_kinematics_np(self, other) @ other.collision[0].origin.to_np())[:3, 3],
                    k=1)[1]
            closest_vert = self.collision[0].mesh.vertices[closest_vert_id]

            # Compute the closest faces on the other body to the closes vertex
            faces = nearby_faces(other.collision[0].mesh,
                                 [(self._world.compute_forward_kinematics_np(other, self) @ self.collision[
                                     0].origin.to_np())[:3, 3] + closest_vert])[0]
            face_weights = np.zeros(len(other.collision[0].mesh.faces))

            # Assign weights to the faces based on a geometric distribution
            face_weights[faces] = evaluated_geometric_distribution(len(faces))

            # Sample points on the surface of the other body
            q = sample_surface(other.collision[0].mesh, sample_size, face_weight=face_weights, seed=420)[0]
            # Make 4x4 transformation matrix from points
            points = np.tile(np.eye(4, dtype=np.float32), (len(q), 1, 1))
            points[:, :3, 3] = q

            # Transform from the mesh to the other mesh
            transform = np.linalg.inv(self.collision[0].origin.to_np()) @ self._world.compute_forward_kinematics_np(
                self, other) @ other.collision[0].origin.to_np()
            points = points @ transform

            points = points[:, :3, 3]  # Extract the points from the transformation matrix

            query_points.extend(points)

        # Actually compute the closest points
        points, dists = closest_point(self.collision[0].mesh, query_points)[:2]
        # Find the closest points for each body out of all the sampled points
        points = np.array(points).reshape(len(others), sample_size, 3)
        dists = np.array(dists).reshape(len(others), sample_size)
        dist_min = np.min(dists, axis=1)
        points_min_self = points[np.arange(len(others)), np.argmin(dists, axis=1), :]
        points_min_other = np.array(query_points).reshape(len(others), sample_size, 3)[np.arange(len(others)),
                           np.argmin(dists, axis=1), :]
        return points_min_self, points_min_other, dist_min

    @property
    def child_bodies(self) -> List[Body]:
        """
        Returns the child bodies of this body.
        """
        return self._world.compute_child_bodies(self)

    @property
    def parent_body(self) -> Body:
        """
        Returns the parent body of this body.
        """
        return self._world.compute_parent_body(self)

    @property
    def bounding_box_collection(self) -> BoundingBoxCollection:
        """
        Return the bounding box collection of the link with the given name.
        This method computes the bounding box of the link in world coordinates by transforming the local axis-aligned
        bounding boxes of the link's geometry to world coordinates.

        Note: These bounding boxes may not be disjoint, however the random events library always makes them disjoint. If
        this is the case, and we feed he non-disjoint bounding boxes into the gcs, it may trigger unexpected behavior.

        :return: A BoundingBoxCollection containing the bounding boxes of the link's geometry in world
        """
        world = self._world
        body_transform: ndarray = world.compute_forward_kinematics_np(world.root, self)
        world_bboxes = []

        for shape in self.collision:
            shape_transform: ndarray = shape.origin.to_np()

            world_transform: ndarray = body_transform @ shape_transform
            body_pos = world_transform[:3, 3]
            body_rotation_matrix = world_transform[:3, :3]

            local_bb: BoundingBox = shape.as_bounding_box()

            # Get all 8 corners of the BB in link-local space
            corners = np.array([corner.to_np()[:3] for corner in local_bb.get_points()])  # shape (8, 3)

            # Transform each corner to world space: R * corner + T
            transformed_corners = (corners @ body_rotation_matrix.T) + body_pos

            # Compute world-space bounding box from transformed corners
            min_corner = np.min(transformed_corners, axis=0)
            max_corner = np.max(transformed_corners, axis=0)

            world_bb = BoundingBox.from_min_max(Point3(*min_corner), Point3(*max_corner))
            world_bboxes.append(world_bb)

        return BoundingBoxCollection(world_bboxes)

    @property
    def global_pose(self) -> NpMatrix4x4:
        """
        Computes the pose of the body in the world frame.
        :return: 4x4 transformation matrix.
        """
        return self._world.compute_forward_kinematics_np(self._world.root, self)

    @property
    def parent_connection(self) -> Connection:
        """
        Returns the parent connection of this body.
        """
        return self._world.compute_parent_connection(self)

    @classmethod
    def from_body(cls, body: Body):
        """
        Creates a new link from an existing link.
        """
        new_link = cls(name=body.name, visual=body.visual, collision=body.collision)
        new_link._world = body._world
        new_link.index = body.index
        return new_link


@dataclass
class View(WorldEntity):
    """
    Represents a view on a set of bodies in the world.

    This class can hold references to certain bodies that gain meaning in this context.
    """

    def _bodies(self, visited: Set[int]) -> Set[Body]:
        """
        Recursively collects all bodies that are part of this view.
        """
        stack: Deque[object] = deque([self])
        bodies: Set[Body] = set()

        while stack:
            obj = stack.pop()
            oid = id(obj)
            if oid in visited:
                continue
            visited.add(oid)

            match obj:
                case Body():
                    bodies.add(obj)

                case View():
                    stack.extend(_attr_values(obj))

                case Mapping():
                    stack.extend(v for v in obj.values() if _is_body_view_or_iterable(v))

                case Iterable() if not isinstance(obj, (str, bytes, bytearray)):
                    stack.extend(v for v in obj if _is_body_view_or_iterable(v))

        return bodies

    @property
    def bodies(self) -> Iterable[Body]:
        """
        Returns a Iterable of all relevant bodies in this view. The default behaviour is to aggregate all bodies that are accessible
        through the properties and fields of this view, recursively.
        If this behaviour is not desired for a specific view, it can be overridden by implementing the `bodies` property.
        """
        return self._bodies(set())

    def as_bounding_box_collection(self) -> BoundingBoxCollection:
        """
        Returns a bounding box collection that contains the bounding boxes of all bodies in this view.
        """
        bbs = reduce(
            lambda accumulator, bb_collection: accumulator.merge(bb_collection),
            (body.bounding_box_collection for body in self.bodies if body.has_collision())
        )
        return bbs


@dataclass(unsafe_hash=True)
class RootedView(View):
    """
    Represents a view that is rooted in a specific body.
    """
    root: Body = field(default_factory=Body)


@dataclass(unsafe_hash=True)
class EnvironmentView(RootedView):
    """
    Represents a view of the environment.
    """

    @property
    def bodies(self) -> Set[Body]:
        """
        Returns a set of all bodies in the environment view.
        """
        return set(self._world.compute_child_bodies_recursive(self.root)) | {self.root}


@dataclass
class Connection(WorldEntity):
    """
    Represents a connection between two bodies in the world.
    """

    parent: Body
    """
    The parent body of the connection.
    """

    child: Body
    """
    The child body of the connection.
    """

    origin_expression: TransformationMatrix = field(default=None)
    """
    A symbolic expression describing the origin of the connection.
    """

    def __post_init__(self):
        if self.origin_expression is None:
            self.origin_expression = TransformationMatrix()
        self.origin_expression.reference_frame = self.parent
        self.origin_expression.child_frame = self.child
        if self.name is None:
            self.name = PrefixedName(f'{self.parent.name.name}_T_{self.child.name.name}', prefix=self.child.name.prefix)

    def _post_init_world_part(self):
        """
        Executes post-initialization logic based on the presence of a world attribute.
        """
        if self._world is None:
            self._post_init_without_world()
        else:
            self._post_init_with_world()

    def _post_init_with_world(self):
        """
        Initialize or perform additional setup operations required after the main
        initialization step. Use for world-related configurations or specific setup
        details required post object creation.
        """
        pass

    def _post_init_without_world(self):
        """
        Handle internal initialization processes when _world is None. Perform
        operations post-initialization for internal use only.
        """
        pass

    def __hash__(self):
        return hash((self.parent, self.child))

    def __eq__(self, other):
        return self.name == other.name

    @property
    def origin(self) -> cas.TransformationMatrix:
        """
        :return: The relative transform between the parent and child frame.
        """
        return self._world.compute_forward_kinematics(self.parent, self.child)

    # @lru_cache(maxsize=None)
    def origin_as_position_quaternion(self) -> Expression:
        position = self.origin_expression.to_position()[:3]
        orientation = self.origin_expression.to_quaternion()
        return cas.vstack([position, orientation]).T


def _is_body_view_or_iterable(obj: object) -> bool:
    """
    Determines if an object is a Body, a View, or an Iterable (excluding strings and bytes).
    """
    return (
            isinstance(obj, (Body, View)) or
            (isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, bytearray)))
    )


def _attr_values(view: View) -> Iterable[object]:
    """
    Yields all dataclass fields and set properties of this view.
    Skips private fields (those starting with '_'), as well as the 'bodies' property.

    :param view: The view to extract attributes from.
    """
    for f in fields(view):
        if f.name.startswith('_'):
            continue
        v = getattr(view, f.name, None)
        if _is_body_view_or_iterable(v):
            yield v

    for name, prop in inspect.getmembers(type(view), lambda o: isinstance(o, property)):
        if name == "bodies" or name.startswith('_'):
            continue
        try:
            v = getattr(view, name)
        except Exception:
            continue
        if _is_body_view_or_iterable(v):
            yield v
