"""
@author: Harry J.E Day <harry@dayfamilyweb.com>
@date: 27/08/17
@copyright: Harry J.E Day 2017.
@summary: very simple email book data structures
"""
from google.appengine.ext import ndb


class AddressEntry(ndb.Model):

    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)


    def to_json_dict(self):
        """
        converts the email entry into a json serializable dict
        :return: a dictionary representing this model instance
        :rtype: dict
        """
        return {
            "id" : self.key.urlsafe(),
            "name": self.name,
            "email": self.email
        }

    @staticmethod
    def get_all_addresses(limit, paginated=False, cursor_key=None):
        """
        get all addresses in the email book
        :param limit: the limit on the number to return
        :param paginated: if we should return a key for pagination
        :param cursor_key: the key of the cursor if we are on a later page
        :return: json serialisable dict representing all the emailes
        """

        if paginated and cursor_key:
            cursor = ndb.Cursor(urlsafe=cursor_key)
        else:
            cursor = ndb.Cursor()

        results, next_cursor, is_more = AddressEntry.query().fetch_page(limit, start_cursor=cursor)

        jdict = {
            "entries" : [entry.to_json_dict() for entry in results],
            "is_more" : is_more
        }

        if  paginated:
            jdict["next"] = cursor.urlsafe()

        return jdict


    @staticmethod
    def json_to_model(jdict, put=True):
        """
        Converts a dictionary to the model
        :param jdict: json serialisable dictionary to put
        :param put: if we should store it or not
        :return: tuple of bool (succes) and the model object or error message
        """

        if not ("name" in jdict and "email" in jdict):
            return False, "missing fields"

        model = AddressEntry(
            id=jdict["email"], # use the email for id, it makes conflict checking much simpler
            name=jdict["name"],
            email=jdict["email"]
        )

        if put:
            model.put()
        return True, model


    @staticmethod
    @ndb.transactional(xg=True)
    def update_model(key, jdict, put=True):
        """
        Converts a dictionary to the model
        :param key: the key to retrive
        :param jdict: json serialisable dictionary to put
        :param put: if we should store it or not
        :return: tuple of bool (succes) and the model object or error code
        """
        key = ndb.Key(urlsafe=key)
        model = key.get()
        if model is None:
            return False, 404

        if "email" in jdict:
            model.email = jdict["email"]
            # note this operation changes the entity's key
            model.key.delete()
            model.key = ndb.Key(AddressEntry, model.email)

        if "name" in jdict:
            model.name = jdict["name"]

        if put:
            model.put()
        return True, model


