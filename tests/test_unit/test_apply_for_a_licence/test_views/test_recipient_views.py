from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestDeleteRecipientView:
    def test_successful_post(self, afal_client):
        request = RequestFactory().post("/")
        request.session = afal_client.session
        request.session["recipients"] = data.recipients
        recipient_id = "recipient1"
        request.session.save()
        response = afal_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": recipient_id},
        )
        assert "recipient1" not in afal_client.session["recipients"].keys()
        assert afal_client.session["recipients"] != data.recipients
        assert response.url == "/apply-for-a-licence/recipient_added"
        assert response.status_code == 302

    def test_cannot_delete_all_recipients_post(self, afal_client):
        request = RequestFactory().post("/")
        request.session = afal_client.session
        request.session["recipients"] = data.recipients
        request.session.save()
        response = afal_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": "recipient1"},
        )
        response = afal_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": "recipient2"},
        )
        response = afal_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": "recipient3"},
        )
        # does not delete last recipient
        assert len(afal_client.session["recipients"]) == 1
        assert "recipient3" in afal_client.session["recipients"].keys()
        assert response.url == "/apply-for-a-licence/recipient_added"
        assert response.status_code == 302

    def test_unsuccessful_post(self, afal_client):
        request_object = RequestFactory().get("/")
        request_object.session = afal_client.session
        request_object.session["recipients"] = data.recipients
        request_object.session.save()
        response = afal_client.post(
            reverse("delete_recipient"),
        )
        assert afal_client.session["recipients"] == data.recipients
        assert response.url == "/apply-for-a-licence/recipient_added"
        assert response.status_code == 302
