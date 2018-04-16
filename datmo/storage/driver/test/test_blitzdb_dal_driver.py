"""
Tests for blitzdb_dal_driver.py
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil
import tempfile

from datmo.storage.driver.blitzdb_dal_driver import BlitzDBDALDriver
from datmo.util.exceptions import EntityNotFound


class TestBlitzDBInit():
    """
    Checks init of TestBlitzDB
    """
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_file_db_init(self):
        database = BlitzDBDALDriver("file", self.temp_dir)
        assert database != None

    def test_remote_db_init(self):
        mongo_connection = "mongodb://localhost:27017"
        # Make mongo db connection required for testing?
        database = BlitzDBDALDriver("service", mongo_connection)
        assert database != None


class TestBlitzDB():
    """
    Checks all functions of the TestBlitzDB
    """

    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        # TODO: Automatically create Document class from collection
        # For now, use one of pre-defined collections:
        # model, datmo_session, datmo_task, datmo_snapshot, datmo_user
        self.collection = 'model'
        self.database = BlitzDBDALDriver("file", self.temp_dir)

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_filebased_db(self):
        assert self.database != None

    def test_db_set(self):
        test_obj = {"foo": "bar"}
        result = self.database.set(self.collection, test_obj)
        assert result.get('id') != None

    def test_db_get(self):
        test_obj = {"foo": "bar_1"}
        result = self.database.set(self.collection, test_obj)
        result1 = self.database.get(self.collection, result.get('id'))
        assert result1.get('id') == result.get('id')

    def test_db_update(self):
        test_obj = {"foo": "bar_2"}
        result = self.database.set(self.collection, test_obj)
        test_obj2 = {
            "id": result.get('id'),
            "foo": "bar_3"
        }
        result2 = self.database.set(self.collection, test_obj2)
        assert result.get('id') == result2.get('id')
        assert result2.get('foo') == "bar_3"

    def test_db_query(self):
        test_obj = {"foo": "bar"}
        results = self.database.query(self.collection, test_obj)
        assert len(results) == 1

    def test_db_exists(self):
        test_obj = {"foo": "bar_2"}
        result = self.database.set(self.collection, test_obj)
        assert self.database.exists(self.collection, result.get('id'))
        assert not self.database.exists(self.collection, 'not_found')

    def test_db_query_all(self):
        results = self.database.query(self.collection, {})
        assert len(results) == 4
        # ensure each entity returns an 'id'
        for entity in results:
            assert entity['id'] != None

    def test_raise_entity_not_found(self):
        exp_thrown = False
        try:
            result = self.database.get(self.collection, 'not_found')
        except EntityNotFound:
            exp_thrown = True
        assert exp_thrown

    def test_delete_entity(self):
        test_obj = {"name": "delete_me"}
        obj_to_delete = self.database.set(self.collection, test_obj)
        result = self.database.delete(self.collection, obj_to_delete.get('id'))
        exp_thrown = False
        try:
            result = self.database.get(self.collection, obj_to_delete.get('id'))
        except EntityNotFound:
            exp_thrown = True
        assert exp_thrown

    def test_document_type_2(self):
        """
        Collections are associated to a specific class, so
        this should fail
        """

        test_obj = {"car": "baz"}
        collection_2 = self.collection + '_2'
        thrown = False
        try:
            result = self.database.set(collection_2, test_obj)
        except:
            thrown =True
        assert thrown


