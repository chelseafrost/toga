from travertino.size import at_least

from ..libs import android_widgets
from .base import Widget


class DetailedList(Widget):
    def create(self):
        # DetailedList is not a specific widget on Android, so we build it out
        # of a few pieces.
        parent = android_widgets.LinearLayout(self._native_activity)
        parent.setOrientation(android_widgets.LinearLayout.VERTICAL)
        self.native = parent
        scroll_view = android_widgets.ScrollView(self._native_activity)
        scroll_view_layout_params = android_widgets.LinearLayout__LayoutParams(
                android_widgets.LinearLayout__LayoutParams.MATCH_PARENT,
                android_widgets.LinearLayout__LayoutParams.MATCH_PARENT
        )
        scroll_view_layout_params.gravity = android_widgets.Gravity.TOP
        parent.addView(scroll_view, scroll_view_layout_params)
        dismissable_container = android_widgets.LinearLayout(self._native_activity)
        dismissable_container.setOrientation(android_widgets.LinearLayout.VERTICAL)
        dismissable_container_params = android_widgets.LinearLayout__LayoutParams(
                android_widgets.LinearLayout__LayoutParams.MATCH_PARENT,
                android_widgets.LinearLayout__LayoutParams.MATCH_PARENT
        )
        scroll_view.addView(
                dismissable_container, dismissable_container_params
        )
        for i in range(len((self.interface.data or []))):
            self._make_row(dismissable_container, i)

    def _make_row(self, container, i):
        # Create the foreground.
        row_foreground = android_widgets.RelativeLayout(self._native_activity)
        row_foreground.setBackgroundColor(self._native_activity.getResources().getColor(
            android_widgets.R__color.background_light))
        container.addView(row_foreground)

        # Add user-provided icon to layout.
        icon_image_view = android_widgets.ImageView(self._native_activity)
        icon = self.interface.data[i].icon
        icon.bind(self.interface.factory)
        bitmap = android_widgets.BitmapFactory.decodeFile(str(icon._impl.path))
        if bitmap is not None:
            icon_image_view.setImageBitmap(bitmap)
        icon_layout_params = android_widgets.RelativeLayout__LayoutParams(
            android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT,
            android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT)
        icon_layout_params.width = 150
        icon_layout_params.setMargins(25, 0, 25, 0)
        icon_layout_params.height = 250
        icon_image_view.setScaleType(android_widgets.ImageView__ScaleType.FIT_CENTER)
        row_foreground.addView(icon_image_view, icon_layout_params)

        # Create layout to show top_text and bottom_text.
        text_container = android_widgets.LinearLayout(self._native_activity)
        text_container_params = android_widgets.RelativeLayout__LayoutParams(
                android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT,
                android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT)
        text_container_params.height = 250
        text_container_params.setMargins(25 + 25 + 150, 0, 0, 0)
        row_foreground.addView(text_container, text_container_params)
        text_container.setOrientation(android_widgets.LinearLayout.VERTICAL)
        text_container.setWeightSum(2.0)

        # Create top & bottom text; add them to layout.
        top_text = android_widgets.TextView(self._native_activity)
        top_text.setText(str(getattr(self.interface.data[i], 'title', '')))
        top_text.setTextSize(20.0)
        top_text.setTextColor(self._native_activity.getResources().getColor(android_widgets.R__color.black))
        bottom_text = android_widgets.TextView(self._native_activity)
        bottom_text.setTextColor(self._native_activity.getResources().getColor(android_widgets.R__color.black))
        bottom_text.setText(str(getattr(self.interface.data[i], 'subtitle', '')))
        bottom_text.setTextSize(16.0)
        top_text_params = android_widgets.LinearLayout__LayoutParams(
                android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT,
                android_widgets.RelativeLayout__LayoutParams.MATCH_PARENT)
        top_text_params.weight = 1.0
        top_text.setGravity(android_widgets.Gravity.BOTTOM)
        text_container.addView(top_text, top_text_params)
        bottom_text_params = android_widgets.LinearLayout__LayoutParams(
                android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT,
                android_widgets.RelativeLayout__LayoutParams.MATCH_PARENT)
        bottom_text_params.weight = 1.0
        bottom_text.setGravity(android_widgets.Gravity.TOP)
        bottom_text_params.gravity = android_widgets.Gravity.TOP
        text_container.addView(bottom_text, bottom_text_params)

    def change_source(self, source):
        # If the source changes, re-build the widget.
        self.create()

    def set_on_refresh(self, *args, **kwargs):
        # This widget does not yet support pull-to-refresh.
        self.interface.factory.not_implemented("DetailedList.set_on_refresh()")

    def after_on_refresh(self):
        # This widget does not yet support pull-to-refresh.
        self.interface.factory.not_implemented("DetailedList.after_on_refresh()")

    def insert(self, index, item):
        # If the data changes, re-build the widget. Brutally effective.
        self.create()

    def change(self, item):
        # If the data changes, re-build the widget. Brutally effective.
        self.create()

    def remove(self, item):
        # If the data changes, re-build the widget. Brutally effective.
        self.create()

    def clear(self):
        # If the data changes, re-build the widget. Brutally effective.
        self.create()

    def set_on_select(self, handler):
        # This widget currently does not implement any handlers for user touch.
        self.interface.factory.not_implemented("DetailedList.set_on_select()")

    def set_on_delete(self, handler):
        # This widget currently does not implement event handlers for data chance.
        self.interface.factory.not_implemented("DetailedList.set_on_delete()")

    def scroll_to_row(self, row):
        # This widget cannot currently scroll to a specific row.
        self.interface.factory.not_implemented("DetailedList.scroll_to_row()")

    def rehint(self):
        # Android can crash when rendering some widgets until they have their layout params set. Guard for that case.
        if self.native.getLayoutParams() is None:
            return
        self.native.measure(
            android_widgets.View__MeasureSpec.UNSPECIFIED,
            android_widgets.View__MeasureSpec.UNSPECIFIED,
        )
        self.interface.intrinsic.width = at_least(self.native.getMeasuredWidth())
        self.interface.intrinsic.height = self.native.getMeasuredHeight()
