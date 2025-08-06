from django.conf import settings
from django.contrib.auth import get_permission_codename
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import localize
from django.utils.translation import gettext as _

from cms.models import PageContent
from cms.toolbar.items import Break, ButtonList, ModalButton
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from djangocms_versioning import constants, versionables
from djangocms_versioning.cms_toolbars import VERSIONING_MENU_IDENTIFIER
from djangocms_versioning.models import Version


def _get_published_page_version(self):
    language = self.current_lang

    # Exit the current toolbar object is not a Page / PageContent instance
    if not isinstance(self.toolbar.obj, PageContent) or not self.page:  # pragma: no cover
        return

    return PageContent.objects.filter(
        page=self.page, language=language
    ).select_related("page").first()


@toolbar_pool.register
class TimedPublicationsToolbar(CMSToolbar):
    """
    Toolbar for managing timed publications in the CMS.
    Inherits from CMSToolbar to provide custom functionality.
    """

    def post_template_populate(self):
        """
        Additional actions after the template has been populated.
        """
        super().post_template_populate()
        self.update_versioning_menu()

    def update_versioning_menu(self):
        """Update the versioning menu with timed publication options.
        This method checks if the versioning menu exists and adds
        the timed publications options to it."""

        versioning_menu = self.toolbar.get_menu(VERSIONING_MENU_IDENTIFIER)
        if not versioning_menu:  # pragma: no cover
            return None

        version = Version.objects.get_for_content(self.toolbar.obj)
        # Visibility is only valid for published versions
        visibility = version.state == constants.PUBLISHED and getattr(version, 'visibility', None)
        if version is None:  # pragma: no cover
            return

        # Inform about time restrictions
        if visibility and (visibility.start or visibility.end):
            # Add a break if info fields on time restrictions have been added
            versioning_menu.add_item(Break(), position=0)
        if visibility and visibility.end:
            versioning_menu.add_link_item(
                _("Visible until %(datetime)s (%(tz)s)") %  {"datetime": localize(visibility.end), "tz": visibility.end.tzinfo},
                url="",
                disabled=True,
                position=0,
            )
        if visibility and visibility.start:
            if visibility.start < timezone.now():
                msg = _("Visible since %(datetime)s (%(tz)s)") % {"datetime": localize(visibility.start), "tz": visibility.start.tzinfo}
            else:
                msg = _("Visible after %(datetime)s (%(tz)s)") % {"datetime": localize(visibility.start), "tz": visibility.start.tzinfo}
            versioning_menu.add_link_item(
                msg,
                url="",
                disabled=True,
                position=0,
            )

        if not self.toolbar.edit_mode_active:
            return

        version = version.convert_to_proxy()
        proxy_model = versionables.for_content(version.content).version_model_proxy
        url = reverse(
                        f"admin:{proxy_model._meta.app_label}_{proxy_model.__name__.lower()}_publish",
                        args=(version.pk,)
                    )
        if self.request.user.has_perm(
            "{app_label}.{codename}".format(
                app_label=version._meta.app_label,
                codename=get_permission_codename("change", version._meta),
            )
        ) and not getattr(settings, "DJANGOCMS_TIMED_PUBLISHING_BUTTON", False):
            # Timed publishibng
            if version.check_publish.as_bool(self.request.user):
                prev_entry = versioning_menu.find_first(Break)
                prev_entry = versioning_menu.add_modal_item(
                    _("Publish with time limits"),
                    url=url,
                    on_close="REFRESH_PAGE",
                    position=prev_entry,
                )
                prev_entry = versioning_menu.add_item(Break(), position=prev_entry)
        else:
            self._update_publish_button(url)

    def _update_publish_button(self, url: str):
        """Update the publish button to show modal instead of directly publishing."""
        for button_list in self.toolbar.get_right_items():
            if isinstance(button_list, ButtonList):
                for i, button in enumerate(button_list.buttons):
                    if button.url == url:
                        button_list.buttons[i] = ModalButton(
                            button.name,
                            url=button.url,
                            on_close="REFRESH_PAGE",
                            disabled=button.disabled,
                            extra_classes=["cms-btn-action"],
                        )
                        return
