from django.test import TestCase
from django.urls import reverse, resolve


class TestHumanReadableDetailsRouteResolution(TestCase):
    def test_resolves_reference_number_lettercode(self):
        resolver = resolve("/catalogue/CP/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "CP")

    def test_resolves_reference_number_with_space(self):
        resolver = resolve("/catalogue/PROB/1/4/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "PROB 1/4")

    def test_resolves_with_longest_reference_number(self):
        resolver = resolve(
            "/catalogue/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/"
        )

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(
            resolver.kwargs["reference_number"],
            "LAB 2/1782/SandER106/1934/Part25and27-28and30to32",
        )


class TestHumanReadableDetailsURL(TestCase):
    def test_reverse_reference_number_lettercode(self):
        url = reverse("details-page-human-readable", kwargs={"reference_number": "CP"})

        self.assertEqual(url, "/catalogue/CP/")

    def test_reverse_reference_number_with_space(self):
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

        self.assertEqual(resolver.view_name, "details-page-human-readable-with-pseudo-reference")
        self.assertEqual(resolver.kwargs["reference_number"], "CP")
        self.assertEqual(resolver.kwargs["pseudo_reference"], 3)

    def test_resolves_reference_number_with_space(self):
        resolver = resolve("/catalogue/PROB/1/4/~3/")

        self.assertEqual(resolver.view_name, "details-page-human-readable-with-pseudo-reference")
        self.assertEqual(resolver.kwargs["reference_number"], "PROB 1/4")
        self.assertEqual(resolver.kwargs["pseudo_reference"], 3)

    def test_resolves_with_longest_reference_number(self):
        resolver = resolve(
            "/catalogue/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/~3/"
        )

        self.assertEqual(resolver.view_name, "details-page-human-readable-with-pseudo-reference")
        self.assertEqual(
            resolver.kwargs["reference_number"],
            "LAB 2/1782/SandER106/1934/Part25and27-28and30to32",
        )
        self.assertEqual(resolver.kwargs["pseudo_reference"], 3)


class TestHumanReadableDetailsWithPseudoReferenceURL(TestCase):
    def test_reverse_reference_number_lettercode(self):
        url = reverse(
            "details-page-human-readable-with-pseudo-reference",
            kwargs={"reference_number": "CP", "pseudo_reference": 3},
        )

        self.assertEqual(url, "/catalogue/CP/~3/")

    def test_reverse_reference_number_with_space(self):
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

        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["iaid"], "C7810139")


class TestMachineReadableDetailsURL(TestCase):
    def test_reverse_reference_number_lettercode(self):
        url = reverse("details-page-machine-readable", kwargs={"iaid": "C7810139"})

        self.assertEqual(url, "/catalogue/C7810139/")
