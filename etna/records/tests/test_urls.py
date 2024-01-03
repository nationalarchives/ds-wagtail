from django.test import TestCase
from django.urls import resolve, reverse


class TestHumanReadableDetailsRouteResolution(TestCase):
    def test_resolves_reference_number_lettercode(self):
        resolver = resolve("/catalogue/ref/CP/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "CP")

    def test_resolves_lower_case_reference_number_lettercode(self):
        resolver = resolve("/catalogue/ref/cp/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "cp")

    def test_resolves_reference_number(self):
        resolver = resolve("/catalogue/ref/PROB/1/4/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "PROB/1/4")

    def test_resolves_lower_case_reference_number(self):
        resolver = resolve("/catalogue/ref/prob/1/4/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "prob/1/4")

    def test_resolves_with_longest_reference_number(self):
        resolver = resolve(
            "/catalogue/ref/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/"
        )

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(
            resolver.kwargs["reference_number"],
            "LAB/2/1782/SandER106/1934/Part25and27-28and30to32",
        )

    def test_resolves_lower_case_with_longest_reference_number(self):
        resolver = resolve(
            "/catalogue/ref/lab/2/1782/sander106/1934/part25and27-28and30to32/"
        )

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(
            resolver.kwargs["reference_number"],
            "lab/2/1782/sander106/1934/part25and27-28and30to32",
        )


class TestHumanReadableDetailsURL(TestCase):
    def test_reverse_reference_number_lettercode(self):
        url = reverse("details-page-human-readable", kwargs={"reference_number": "CP"})

        self.assertEqual(url, "/catalogue/ref/CP/")

    def test_reverse_reference_number(self):
        url = reverse(
            "details-page-human-readable", kwargs={"reference_number": "PROB 1/4"}
        )

        self.assertEqual(url, "/catalogue/ref/PROB/1/4/")

    def test_reverse_with_longest_reference_number(self):
        url = reverse(
            "details-page-human-readable",
            kwargs={
                "reference_number": "LAB 2/1782/SandER106/1934/Part25and27-28and30to32"
            },
        )

        self.assertEqual(
            url, "/catalogue/ref/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/"
        )


class TestHumanReadableDetailsWithPseudoReferenceRouteResolution(TestCase):
    def test_resolves_reference_number_lettercode(self):
        resolver = resolve("/catalogue/ref/CP/~3/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "CP/~3")

    def test_resolves_reference_number(self):
        resolver = resolve("/catalogue/ref/PROB/1/4/~3/")

        self.assertEqual(resolver.view_name, "details-page-human-readable")
        self.assertEqual(resolver.kwargs["reference_number"], "PROB/1/4/~3")

    def test_resolves_with_longest_reference_number(self):
        resolver = resolve(
            "/catalogue/ref/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/~3/"
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

        self.assertEqual(url, "/catalogue/ref/CP/~3/")

    def test_reverse_reference_number(self):
        url = reverse(
            "details-page-human-readable",
            kwargs={"reference_number": "PROB 1/4/~3"},
        )

        self.assertEqual(url, "/catalogue/ref/PROB/1/4/~3/")

    def test_reverse_with_longest_reference_number(self):
        url = reverse(
            "details-page-human-readable",
            kwargs={
                "reference_number": "LAB 2/1782/SandER106/1934/Part25and27-28and30to32/~3",
            },
        )

        self.assertEqual(
            url, "/catalogue/ref/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/~3/"
        )


class TestMachineReadableDetailsRouteResolution(TestCase):
    def test_resolves_iaid(self):
        resolver = resolve("/catalogue/id/C7810139/")

        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["id"], "C7810139")

    def test_iaid_with_non_standard_prefix(self):
        resolver = resolve("/catalogue/id/C123456/")

        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["id"], "C123456")

    def test_resolves_uuid(self):
        # Some IAIDs are UUIDs. Tested IAID is a real example
        resolver = resolve("/catalogue/id/43f766a9-e968-4b82-93dc-8cf11a841d41/")

        self.assertEqual(resolver.view_name, "details-page-machine-readable")
        self.assertEqual(resolver.kwargs["id"], "43f766a9-e968-4b82-93dc-8cf11a841d41")


class TestMachineReadableDetailsURL(TestCase):
    def test_reverse_iaid(self):
        url = reverse("details-page-machine-readable", kwargs={"id": "C7810139"})

        self.assertEqual(url, "/catalogue/id/C7810139/")

    def test_reverse_uuid(self):
        url = reverse(
            "details-page-machine-readable",
            kwargs={"id": "43f766a9-e968-4b82-93dc-8cf11a841d41"},
        )

        self.assertEqual(url, "/catalogue/id/43f766a9-e968-4b82-93dc-8cf11a841d41/")
