from django.test import TestCase
from django.urls import reverse, resolve

from .. import views


class TestHumanReadableDetailsRouteResolution(TestCase):
    def test_resolves_reference_number_lettercode(self):
        resolver = resolve("/catalogue/CP/")

        self.assertEquals(resolver.func, views.record_page_disambiguation_view)
        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "CP")

    def test_resolves_lower_case_reference_number_lettercode(self):
        resolver = resolve("/catalogue/cp/")

        self.assertEquals(resolver.func, views.record_page_disambiguation_view)
        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "cp")

    def test_resolves_reference_number(self):
        resolver = resolve("/catalogue/PROB/1/4/")

        self.assertEquals(resolver.func, views.record_page_disambiguation_view)
        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "PROB/1/4")

    def test_resolves_lower_case_reference_number(self):
        resolver = resolve("/catalogue/prob/1/4/")

        self.assertEquals(resolver.func, views.record_page_disambiguation_view)
        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "prob/1/4")

    def test_resolves_with_longest_reference_number(self):
        resolver = resolve(
            "/catalogue/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/"
        )

        self.assertEquals(resolver.func, views.record_page_disambiguation_view)
        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(
            resolver.kwargs["reference_number"],
            "LAB/2/1782/SandER106/1934/Part25and27-28and30to32",
        )

    def test_resolves_lower_case_with_longest_reference_number(self):
        resolver = resolve(
            "/catalogue/lab/2/1782/sander106/1934/part25and27-28and30to32/"
        )

        self.assertEquals(resolver.func, views.record_page_disambiguation_view)
        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(
            resolver.kwargs["reference_number"],
            "lab/2/1782/sander106/1934/part25and27-28and30to32",
        )


class TestHumanReadableDetailsURL(TestCase):
    def test_reverse_reference_number_lettercode(self):
        url = reverse("details-page-human-readable", kwargs={"reference_number": "CP"})

        self.assertEqual(url, "/catalogue/CP/")

    def test_reverse_reference_number(self):
        url = reverse(
            "details-page-human-readable", kwargs={"reference_number": "PROB 1/4"}
        )

        self.assertEqual(url, "/catalogue/PROB/1/4/")

    def test_reverse_with_longest_reference_number(self):
        url = reverse(
            "details-page-human-readable",
            kwargs={
                "reference_number": "LAB 2/1782/SandER106/1934/Part25and27-28and30to32"
            },
        )

        self.assertEqual(
            url, "/catalogue/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/"
        )


class TestHumanReadableDetailsWithPseudoReferenceRouteResolution(TestCase):
    def test_resolves_reference_number_lettercode(self):
        resolver = resolve("/catalogue/CP/~3/")

        self.assertEqual(
            resolver.view_name, "details-page-human-readable-with-pseudo-reference"
        )
        self.assertEqual(resolver.kwargs["reference_number"], "CP")
        self.assertEqual(resolver.kwargs["pseudo_reference"], 3)

    def test_resolves_reference_number(self):
        resolver = resolve("/catalogue/PROB/1/4/~3/")

        self.assertEqual(
            resolver.view_name, "details-page-human-readable-with-pseudo-reference"
        )
        self.assertEqual(resolver.kwargs["reference_number"], "PROB/1/4")
        self.assertEqual(resolver.kwargs["pseudo_reference"], 3)

    def test_resolves_with_longest_reference_number(self):
        resolver = resolve(
            "/catalogue/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/~3/"
        )

        self.assertEqual(
            resolver.view_name, "details-page-human-readable-with-pseudo-reference"
        )
        self.assertEqual(
            resolver.kwargs["reference_number"],
            "LAB/2/1782/SandER106/1934/Part25and27-28and30to32",
        )
        self.assertEqual(resolver.kwargs["pseudo_reference"], 3)


class TestHumanReadableDetailsWithPseudoReferenceURL(TestCase):
    def test_reverse_reference_number_lettercode(self):
        url = reverse(
            "details-page-human-readable-with-pseudo-reference",
            kwargs={"reference_number": "CP", "pseudo_reference": 3},
        )

        self.assertEqual(url, "/catalogue/CP/~3/")

    def test_reverse_reference_number(self):
        url = reverse(
            "details-page-human-readable-with-pseudo-reference",
            kwargs={"reference_number": "PROB 1/4", "pseudo_reference": 3},
        )

        self.assertEqual(url, "/catalogue/PROB/1/4/~3/")

    def test_reverse_with_longest_reference_number(self):
        url = reverse(
            "details-page-human-readable-with-pseudo-reference",
            kwargs={
                "reference_number": "LAB 2/1782/SandER106/1934/Part25and27-28and30to32",
                "pseudo_reference": 3,
            },
        )

        self.assertEqual(
            url, "/catalogue/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/~3/"
        )


class TestMachineReadableDetailsRouteResolution(TestCase):
    def test_resolves_iaid(self):
        resolver = resolve("/catalogue/C7810139/")

        self.assertEquals(resolver.func, views.record_page_view)
        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["iaid"], "C7810139")

    def test_lower_case_iaid(self):
        resolver = resolve("/catalogue/c123456/")

        self.assertEquals(resolver.func, views.record_page_view)
        self.assertEquals(resolver.view_name, "details-page-machine-readable")


class TestMachineReadableDetailsURL(TestCase):
    def test_reverse_reference_number_lettercode(self):
        url = reverse("details-page-machine-readable", kwargs={"iaid": "C7810139"})

        self.assertEqual(url, "/catalogue/C7810139/")
