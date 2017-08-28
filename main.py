import csv
import json
import logging

import webapp2
from google.appengine.ext import ndb

from address_data import AddressEntry

DEFAULT_PAGE_LIMIT = 500


class SimpleRestAddressHandler(webapp2.RequestHandler):
    """
    A simple rest style address handler
    """

    def get(self, key):
        key = ndb.Key(urlsafe=key)
        model = key.get()
        if not model is None:
            jdict = model.to_json_dict()
            self.response.write(json.dumps(jdict))
        else:
            # no key means its not found
            self.error(404)

    def post(self, key):
        """
        Updates an address
        :param key: the key to update
        """
        request = json.loads(self.request.body)
        success, model_or_code = AddressEntry.update_model(key, request)
        if not success:
            self.error(model_or_code)
            return

        dict = model_or_code.to_json_dict()
        self.response.write(json.dumps(dict))




class SimpleResetAddressesHandler(webapp2.RequestHandler):
    """
    The other part of the rest handler
    """

    def get(self):
        """
        Gets the list of addresses
        """

        limit = self.request.get("limit", DEFAULT_PAGE_LIMIT)
        paginate = self.request.get("paginate", False)
        cursor = self.request.get("cursor", None)

        jdict = AddressEntry.get_all_addresses(limit, paginate, cursor)
        self.response.write(json.dumps(jdict))

    def post(self):
        """
        Adds to the list of addresses. Accepts a csv in the format email, name
        """
        outdict = {"entries":[], "conflict_entries":[]}

        if not "file" in self.request.POST:
            self.error(400)
            outdict = {"errors" : ["Your file seems to be malformed, please make sure it is a csv file formated: name, address"]}
        else:
            file = self.request.POST.get("file")
            csv.register_dialect("strict_csv", delimiter=",", quotechar='"', quoting = csv.QUOTE_MINIMAL, strict=True)
            reader = csv.reader(file.file, dialect="strict_csv")

            row_num = 0
            try:
                for row in reader:
                    row_num+=1
                    # check we have the right number of fields
                    if len(row) != 2:
                        self.error(400)
                        outdict["errors"] = ["row %d does not have two colls!" % row_num]
                        break
                    success, output = AddressEntry.check_and_add(row[0], row[1])
                    if success:
                        outdict["entries"].append(output)
                    else:
                        outdict["conflict_entries"].append(output)
            except csv.Error as ex:
                outdict["errors"] = ["It appears your file is malformed: %s" % ex.message]
                self.error(400)
        self.response.write(json.dumps(outdict))



        pass

    def put(self):
        """
        Creates a new address
        """
        success, model = AddressEntry.json_to_model(json.loads(self.request.body))

        if not success:
            # log the error message
            logging.error(model)
            self.error(400) # bad request
            return

        jdict = model.to_json_dict()
        self.response.write(json.dumps(jdict))


app = webapp2.WSGIApplication([
    (r'/address', SimpleResetAddressesHandler),
    (r'/address/(.+)', SimpleRestAddressHandler)
], debug=True)
