import flet as ft
import os

IS_BUILT = bool(os.getenv('FLET_PLATFORM'))

if IS_BUILT:
    class Cacheimg(ft.Image):
        """
        A control that displays an image.

        Example:
        ```
        import flet as ft

        def main(page: ft.Page):
            page.title = "Image Example"

            img = ft.Image(
                src=f"/icons/icon-512.png",
                width=100,
                height=100,
                fit=ft.ImageFit.CONTAIN,
            )

            page.add(img)

        ft.app(target=main)
        ```

        -----

        Online docs: https://flet.dev/docs/controls/image
        """

        def _get_control_name(self):
            return "flet_cacheimg"

    class CacheCircleAvatar(ft.CircleAvatar):
        """
        A circle that represents a user.

        If `foreground_image_src` fails then `background_image_src` is used. If `background_image_src` fails too,
        then `bgcolor` is used.

        Example:
        ```
        import flet as ft

        def main(page):
            # a "normal" avatar with background image
            a1 = ft.CircleAvatar(
                foreground_image_src="https://avatars.githubusercontent.com/u/5041459?s=88&v=4",
                content=ft.Text("FF"),
            )
            # avatar with failing foreground image and fallback text
            a2 = ft.CircleAvatar(
                foreground_image_src="https://avatars.githubusercontent.com/u/_5041459?s=88&v=4",
                content=ft.Text("FF"),
            )
            # avatar with icon, aka icon with inverse background
            a3 = ft.CircleAvatar(
                content=ft.Icon(ft.icons.ABC),
            )
            # avatar with icon and custom colors
            a4 = ft.CircleAvatar(
                content=ft.Icon(ft.icons.WARNING_ROUNDED),
                color=ft.colors.YELLOW_200,
                bgcolor=ft.colors.AMBER_700,
            )
            # avatar with online status
            a5 = ft.Stack(
                [
                    ft.CircleAvatar(
                        foreground_image_src="https://avatars.githubusercontent.com/u/5041459?s=88&v=4"
                    ),
                    ft.Container(
                        content=ft.CircleAvatar(bgcolor=ft.colors.GREEN, radius=5),
                        alignment=ft.alignment.bottom_left,
                    ),
                ],
                width=40,
                height=40,
            )
            page.add(a1, a2, a3, a4, a5)


        ft.app(target=main)
        ```

        -----

        Online docs: https://flet.dev/docs/controls/circleavatar
        """

        def _get_control_name(self):
            return "flet_cache_circle_avatar"

else:
    class Cacheimg(ft.Image):
        pass

    class CacheCircleAvatar(ft.CircleAvatar):
        pass
