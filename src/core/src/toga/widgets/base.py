import warnings
from builtins import id as identifier

from travertino.node import Node

from toga.platform import get_platform_factory
from toga.style import Pack, TogaApplicator


class WidgetRegistry(dict):
    # WidgetRegistry is implemented as a subclass of dict, because it provides
    # a mapping from ID to widget. However, it exposes a set-like API; add()
    # and update() take instances to be added, and iteration is over values.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        # We do not want to allow setting items directly but to use the "add"
        # method instead.
        raise RuntimeError("WidgetRegistry does not allow using item settings directly")

    def update(self, widgets):
        for widget in widgets:
            self.add(widget)

    def add(self, widget):
        if widget.id in self:
            # Prevent from adding the same widget twice
            # or adding 2 widgets with the same id
            raise KeyError(f'There is already a widget with "{widget.id}" id')
        super().__setitem__(widget.id, widget)

    def remove(self, id):
        del self[id]

    def __iter__(self):
        return iter(self.values())


class Widget(Node):
    """This is the base widget implementation that all widgets in Toga derive
    from.

    It defines the interface for core functionality for children, styling,
    layout and ownership by specific App and Window.

    Apart from the above, this is an abstract implementation which must
    be made concrete by some platform-specific code for the _apply_layout
    method.

    Args:
        id (str): An identifier for this widget.
        enabled (bool): Whether or not interaction with the button is possible, defaults to `True`.
        style: An optional style object.
            If no style is provided then a new one will be created for the widget.
    """

    def __init__(
        self,
        id=None,
        enabled=True,
        style=None,
        factory=None,  # DEPRECATED !
    ):
        ######################################################################
        # 2022-09: Backwards compatibility
        ######################################################################
        # factory no longer used
        if factory:
            warnings.warn("The factory argument is no longer used.", DeprecationWarning)
        ######################################################################
        # End backwards compatibility.
        ######################################################################
        super().__init__(
            style=style if style else Pack(), applicator=TogaApplicator(self)
        )

        self._id = str(id) if id else str(identifier(self))
        self._window = None
        self._app = None
        self._impl = None

        self._enabled = enabled

        self.factory = get_platform_factory()

    def __repr__(self):
        return f"<{self.__class__.__name__}:0x{identifier(self):x}>"

    @property
    def id(self):
        """The node identifier. This id can be used to target styling
        directives.

        Returns:
            The widgets identifier as a ``str``.
        """
        return self._id

    def add(self, *children):
        """Add nodes as children of this one. If a node already has a different
        parent, it will be moved over. This does nothing if a node already is a
        child of this node.

        Args:
            children: Nodes to add as children of this node.

        Raises:
            ValueError: If this node is a leaf, and cannot have children.
        """
        for child in children:
            if child.parent is not self:

                # remove from old parent
                if child.parent:
                    child.parent.remove(child)

                # add to new parent
                super().add(child)

                # set app and window
                child.app = self.app
                child.window = self.window

                if self._impl:
                    self._impl.add_child(child._impl)

        if self.window:
            self.window.content.refresh()

    def insert(self, index, child):
        """Insert a node as a child of this one. If the node already has a
        different parent, it will be moved over. This does nothing if the node
        already is a child of this node.

        Args:
            index: Position of child node.
            child: A node to insert as a child of this node.

        Raises:
            ValueError: If this node is a leaf, and cannot have children.
        """
        if child.parent is not self:

            # remove from old parent
            if child.parent:
                child.parent.remove(child)

            # add to new parent
            super().insert(index, child)

            # set app and window
            child.app = self.app
            child.window = self.window

            if self._impl:
                self._impl.insert_child(index, child._impl)

        if self.window:
            self.window.content.refresh()

    def remove(self, *children):
        """Remove child nodes of this node. This does nothing if a given node
        is not a child of this node.

        Args:
            children: Child nodes to remove.

        Raises:
            ValueError: If this node is a leaf, and cannot have children.
        """
        for child in children:
            if child.parent is self:
                super().remove(child)

                child.app = None
                child.window = None

                if self._impl:
                    self._impl.remove_child(child._impl)

        if self.window:
            self.window.content.refresh()

    @property
    def app(self):
        """The App to which this widget belongs. On setting the app we also
        iterate over all children of this widget and set them to the same app.

        Returns:
            The :class:`~toga.App` to which this widget belongs.

        Raises:
            ValueError: If the widget is already associated with another app.
        """
        return self._app

    @app.setter
    def app(self, app):
        # If the widget is already assigned to an app,
        if self._app:
            if app is None:
                # Deregister the widget.
                self._app.widgets.remove(self.id)
            elif self._app != app:
                # raise an error when we already have an app and attempt to override it
                # with a different app
                raise ValueError("Widget %s is already associated with an App" % self)
            else:
                # If app is the same as the previous app, return
                return

        if self._impl:
            self._app = app
            self._impl.set_app(app)
            for child in self.children:
                child.app = app

        if app is not None:
            # Add this widget to the application widget registry
            app.widgets.add(self)

        # Provide an extension point for widgets with
        # more complex widget heirarchies
        self._set_app(app)

    def _set_app(self, app):
        pass

    @property
    def window(self):
        """The Window to which this widget belongs. On setting the window, we
        automatically update all children of this widget to belong to the same
        window.

        Returns:
            The :class:`~toga.Window` to which the widget belongs.
        """
        return self._window

    @window.setter
    def window(self, window):
        # Remove the widget from the widget registry it is currently a part of
        if self.window is not None:
            self.window.widgets.remove(self.id)

        self._window = window
        if self._impl:
            self._impl.set_window(window)

        if self._children is not None:
            for child in self._children:
                child.window = window

        if window is not None:
            # Add this widget to the window's widget registry
            window.widgets.add(self)

        # Provide an extension point for widgets with
        # more complex widget heirarchies
        self._set_window(window)

    def _set_window(self, window):
        pass

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = bool(value)
        self._impl.set_enabled(value)

    def refresh(self):
        """Refresh the layout and appearance of the tree this node is contained
        in."""
        if self._root:
            self._root.refresh()
        else:
            self.refresh_sublayouts()
            super().refresh(self._impl.viewport)

    def refresh_sublayouts(self):
        for child in self.children:
            child.refresh_sublayouts()

    def focus(self):
        if self._impl is not None:
            self._impl.focus()
