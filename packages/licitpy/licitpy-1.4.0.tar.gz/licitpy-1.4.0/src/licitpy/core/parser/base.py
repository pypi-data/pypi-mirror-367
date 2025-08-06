import lxml.html
from lxml.etree import ParserError, XMLSyntaxError
from lxml.html import HtmlElement

from licitpy.core.exceptions import (
    ElementAttributeNotFoundException,
    ElementNotFoundException,
)


class BaseParser:
    def get_html_element(self, html: str) -> HtmlElement:
        try:
            element = lxml.html.fromstring(html)
            return element

        except (ParserError, XMLSyntaxError) as e:
            raise ValueError("Document is empty or invalid") from e

    def get_html_element_by_id(self, html: str, element_id: str) -> HtmlElement:
        """
        Get the HTML element by ID.
        """

        html_element: HtmlElement = self.get_html_element(html)
        element: HtmlElement = html_element.xpath(f'//*[@id="{element_id}"]')

        return element

    def has_element_id(self, html: str, element_id: str) -> bool:
        """Check if the HTML element exists by ID."""

        html_element: HtmlElement = self.get_html_element_by_id(html, element_id)

        return self.html_element_exists(html_element)

    def html_element_exists(self, html_element: HtmlElement) -> bool:
        """Check if the HTML element exists."""

        return len(html_element) != 0

    def get_attribute_by_element_id(
        self, html: str, element_id: str, attribute: str
    ) -> str:
        """
        Get the attribute value by element ID.
        """

        html_element: HtmlElement = self.get_html_element_by_id(html, element_id)

        if not self.html_element_exists(html_element):
            raise ElementNotFoundException(f"Element with ID '{element_id}' not found")

        attribute_elements = html_element[0].xpath(f".//{attribute}")

        if not attribute_elements:
            raise ElementAttributeNotFoundException(
                f"Element with ID '{element_id}' has no attribute '{attribute}'"
            )

        value: str = attribute_elements[0]

        return value.strip()

    def get_text_by_element_id(self, html: str, element_id: str) -> str:
        """
        Get the text value by element ID.
        """

        return self.get_attribute_by_element_id(html, element_id, "text()")

    def get_src_by_element_id(self, html: str, element_id: str) -> str:
        """
        Get the src value by element ID.
        """

        return self.get_attribute_by_element_id(html, element_id, "@src")

    def get_on_click_by_element_id(self, html: str, element_id: str) -> str:
        """
        Get the onclick value by element ID.
        """

        return self.get_attribute_by_element_id(html, element_id, "@onclick")

    def get_href_by_element_id(self, html: str, element_id: str) -> str:
        """
        Get the href value by element ID.
        """

        return self.get_attribute_by_element_id(html, element_id, "@href")

    def get_value_by_element_id(self, html: str, element_id: str) -> str:
        """
        Get the value by element ID.
        """

        return self.get_attribute_by_element_id(html, element_id, "@value")

    def get_view_state(self, html: str) -> str:
        """
        Get the __VIEWSTATE value from the HTML content.
        """

        return self.get_value_by_element_id(html, "__VIEWSTATE")
