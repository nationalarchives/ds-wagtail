from django.test import TestCase
from django.urls import reverse, resolve


class TestHumanReadableDetailsRouteResolution(TestCase):
    def test_resolves_reference_number_lettercode(self):
        resolver = resolve("/catalogue/CP/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "CP")

    def test_resolves_lower_case_reference_number_lettercode(self):
        resolver = resolve("/catalogue/cp/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "cp")

    def test_resolves_reference_number(self):
        resolver = resolve("/catalogue/PROB/1/4/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "PROB/1/4")

    def test_resolves_lower_case_reference_number(self):
        resolver = resolve("/catalogue/prob/1/4/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "prob/1/4")

    def test_resolves_with_longest_reference_number(self):
        resolver = resolve(
            "/catalogue/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/"
        )

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(
            resolver.kwargs["reference_number"],
            "LAB/2/1782/SandER106/1934/Part25and27-28and30to32",
        )

    def test_resolves_lower_case_with_longest_reference_number(self):
        resolver = resolve(
            "/catalogue/lab/2/1782/sander106/1934/part25and27-28and30to32/"
        )

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

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "CP/~3")

    def test_resolves_reference_number(self):
        resolver = resolve("/catalogue/PROB/1/4/~3/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "PROB/1/4/~3")

    def test_resolves_with_longest_reference_number(self):
        resolver = resolve(
            "/catalogue/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/~3/"
        )

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(
            resolver.kwargs["reference_number"],
            "LAB/2/1782/SandER106/1934/Part25and27-28and30to32/~3",
        )


class TestHumanReadableDetailsWithPseudoReferenceURL(TestCase):
    def test_reverse_reference_number_lettercode(self):
        url = reverse(
            "details-page-human-readable",
            kwargs={"reference_number": "CP/~3"},
        )

        self.assertEqual(url, "/catalogue/CP/~3/")

    def test_reverse_reference_number(self):
        url = reverse(
            "details-page-human-readable",
            kwargs={"reference_number": "PROB 1/4/~3"},
        )

        self.assertEqual(url, "/catalogue/PROB/1/4/~3/")

    def test_reverse_with_longest_reference_number(self):
        url = reverse(
            "details-page-human-readable",
            kwargs={
                "reference_number": "LAB 2/1782/SandER106/1934/Part25and27-28and30to32/~3",
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

    def test_lower_case_iaid(self):
        resolver = resolve("/catalogue/c123456/")

        self.assertEquals(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["iaid"], "c123456")

    def test_iaid_with_non_standard_prefix(self):
        resolver = resolve("/catalogue/d123456/")

        self.assertEquals(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["iaid"], "d123456")

    def test_resolves_uuid(self):
        # Some IAIDs are UUIDs. Tested IAID is a real example
        resolver = resolve("/catalogue/43f766a9-e968-4b82-93dc-8cf11a841d41/")

        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(
            resolver.kwargs["iaid"], "43f766a9-e968-4b82-93dc-8cf11a841d41"
        )


class TestMachineReadableDetailsURL(TestCase):
    def test_reverse_iaid(self):
        url = reverse("details-page-machine-readable", kwargs={"iaid": "C7810139"})

        self.assertEqual(url, "/catalogue/C7810139/")

    def test_reverse_uuid(self):
        url = reverse(
            "details-page-machine-readable",
            kwargs={"iaid": "43f766a9-e968-4b82-93dc-8cf11a841d41"},
        )

        self.assertEqual(url, "/catalogue/43f766a9-e968-4b82-93dc-8cf11a841d41/")
