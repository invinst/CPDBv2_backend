from django.db.models import ManyToManyField, CharField, Model
from django.test import TransactionTestCase
from mock import Mock
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from robber import expect

from cms.fields import StringField
from cms.serializers import BaseCMSPageSerializer


class BaseCMSPageSerializerTestCase(TransactionTestCase):
    def setUp(self):
        self.mock_fields = Mock()
        self.mock_fields.add = Mock()
        self.page_model = Mock()
        self.page_model.objects = Mock()
        self.page_model.objects.create = Mock(return_value=Mock(**{'fields': self.mock_fields}))

        class SerializerA(BaseCMSPageSerializer):
            a = StringField(source='fields')

            class Meta:
                model = self.page_model

        class SerializerB(BaseCMSPageSerializer):
            a = serializers.IntegerField()
            b = serializers.IntegerField(write_only=True)
            c = StringField(source='fields')
            d = serializers.IntegerField()

            class Meta:
                model = self.page_model
                meta_fields = ('a', 'b')
                fields = ('c', 'd')

        class SerializerC(BaseCMSPageSerializer):
            a = serializers.IntegerField()
            b = serializers.IntegerField(write_only=True)
            c = serializers.IntegerField(read_only=True)
            d = StringField(fake_value='d')

            class Meta:
                model = self.page_model
                meta_fields = ('a', 'b', 'c', 'd')

        class DummyModel(Model):
            name = CharField(max_length=256)

            class Meta:
                app_label = 'cms'

        class ChildSerializer(ModelSerializer):
            class Meta:
                model = DummyModel
                fields = '__all__'

        class SerializerD(BaseCMSPageSerializer):
            a = ChildSerializer(source='fields', many=True)

            class Meta:
                model = self.page_model
                meta_fields = ('a',)

        class SerializerEmpty(BaseCMSPageSerializer):
            pass

        self.serializer_class_a = SerializerA
        self.serializer_class_b = SerializerB
        self.serializer_class_c = SerializerC
        self.serializer_class_d = SerializerD
        self.serializer_class_empty = SerializerEmpty

    def test_serialize(self):
        page = Mock()
        page.fields = {
            'a_value': 'b'
        }

        serializer = self.serializer_class_a(page)
        self.assertDictEqual(serializer.data['fields'][0], {
            'name': 'a',
            'type': 'string',
            'value': 'b'
        })

        serializer_empty = self.serializer_class_empty(page)
        expect(serializer_empty.data['fields']).to.be.empty()

    def test_serialize_meta_fields(self):
        page = Mock()
        page.fields = {
            'c_value': 'd'
        }
        page.a = 3
        page.b = 1
        page.d = 1
        serializer = self.serializer_class_b(page)
        self.assertEqual(len(serializer.data['fields']), 2)
        self.assertDictEqual(serializer.data['fields'][0], {
            'name': 'c',
            'type': 'string',
            'value': 'd'
        })
        self.assertEqual(serializer.data['fields'][1], 1)
        self.assertEqual(serializer.data['meta'], {'a': 3})

    def test_update(self):
        page = Mock()
        page.fields = {
            'a_value': 'b'
        }
        page.save = Mock()
        serializer = self.serializer_class_a(page, data={'fields': [{'name': 'a', 'type': 'string', 'value': 'c'}]})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertDictEqual(serializer.data['fields'][0], {
            'name': 'a',
            'type': 'string',
            'value': 'c'
        })
        page.save.assert_called()
        self.assertEqual(page.fields['a_value'], 'c')

    def test_update_meta_fields(self):
        page = Mock()
        mock_b = Mock()
        page.fields = {
            'c_value': 'd'
        }
        page.a = 3
        page.b = mock_b
        page.d = 1
        page.save = Mock()
        page._meta.get_field = lambda x: ManyToManyField(Mock()) if x is 'b' else None
        serializer = self.serializer_class_b(page, data={
            'fields': [{'name': 'c', 'type': 'string', 'value': 'd'}],
            'meta': {'a': 4, 'b': 5}
        })

        self.assertTrue(serializer.is_valid())

        serializer.save()

        self.assertDictEqual(serializer.data['fields'][0], {
            'name': 'c',
            'type': 'string',
            'value': 'd'
        })
        page.save.assert_called()
        self.assertEqual(page.fields['c_value'], 'd')
        self.assertEqual(page.a, 4)
        expect(mock_b.set).to.be.called_with(5)

    def test_no_update(self):
        page = Mock()
        page.fields = {
            'c_value': 'd'
        }
        page.a = 3
        page.d = 1
        page.save = Mock()
        serializer = self.serializer_class_b(page, data={'id': 0})
        expect(serializer.is_valid()).to.be.true()
        serializer.save()
        expect(serializer.data['fields'][0]).to.eq({
            'name': 'c',
            'type': 'string',
            'value': 'd'
        })
        page.save.assert_called()
        expect(page.fields['c_value']).to.eq('d')
        expect(page.a).to.eq(3)

    def test_create(self):
        serializer = self.serializer_class_a(data={'fields': [{'name': 'a', 'type': 'string', 'value': 'c'}]})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.page_model.objects.create.assert_called_with(fields={'a_type': 'string', 'a_value': 'c'})

    def test_create_meta_fields(self):
        serializer = self.serializer_class_b(data={
            'fields': [{'name': 'c', 'type': 'string', 'value': 'f'}],
            'meta': {'a': 10}})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.page_model.objects.create.assert_called_with(
            fields={'c_type': 'string', 'c_value': 'f'},
            a=10)

    def test_create_meta_relation_field(self):
        serializer = self.serializer_class_d(data={
            'meta': {'a': [{'name': 'a'}]},
        })

        self.assertTrue(serializer.is_valid())
        serializer.save()
        # import ipdb; ipdb.set_trace();
        expect(self.mock_fields.add).to.be.called_with({'name': 'a'})

    def test_create_empty(self):
        serializer = self.serializer_class_b(data={})
        expect(serializer.is_valid()).to.be.true()
        serializer.save()
        self.page_model.objects.create.assert_called_with()

    def test_fake_data(self):
        fake_data = self.serializer_class_b().fake_data(c='d', d=1, a=4)
        self.assertEqual(len(fake_data['fields']), 2)
        self.assertDictEqual(fake_data['fields'][0], {'name': 'c', 'type': 'string', 'value': 'd'})
        self.assertEqual(fake_data['fields'][1], 1)
        self.assertDictEqual(fake_data['meta'], {'a': 4})

        fake_data = self.serializer_class_c().fake_data(a=1, b=2, c=3)
        self.assertEqual(len(fake_data['meta']), 3)
        self.assertEqual(fake_data['meta']['a'], 1)
        self.assertEqual(fake_data['meta']['b'], 2)
        self.assertDictEqual(fake_data['meta']['d'], {'name': 'd', 'type': 'string', 'value': 'd'})

    def test_deserializing_read_only_field(self):
        class CMSPageSerializer(BaseCMSPageSerializer):
            a = StringField()
            b = serializers.SerializerMethodField()
            c = serializers.IntegerField(read_only=True)

            class Meta:
                model = self.page_model
                meta_fields = ('c',)

            def get_b(self, obj):
                return []

        serializer = CMSPageSerializer(data={'fields': [
            {'name': 'a', 'type': 'string', 'value': 'c'},
            {'name': 'b', 'type': 'string', 'value': 'd'},
        ], 'meta': {'c': 1}})
        self.assertTrue(serializer.is_valid())
        serializer.save()  # does not raise error therefore it did not try to deserialize 'b'

    def test_serializing_write_only_field(self):
        class CMSPageSerializer(BaseCMSPageSerializer):
            a = StringField(source='fields')
            b = StringField(write_only=True)

            class Meta:
                model = self.page_model
        page = Mock()
        page.fields = {
            'a_value': 'b',
            'b_value': 'c'
        }
        serializer = CMSPageSerializer(page)
        self.assertEqual(len(serializer.data['fields']), 1)
        self.assertDictEqual(serializer.data['fields'][0], {
            'name': 'a',
            'type': 'string',
            'value': 'b'
        })

    def test_to_representation_use_fake(self):
        class CMSPageSerializer(BaseCMSPageSerializer):
            a = StringField(source='fields')
            b = StringField(fake_value='c', source='fields')

            class Meta:
                model = self.page_model
                fields = ('a',)
                meta_fields = ('b',)

        page = Mock()
        page.fields = {
            'a_value': 'b'
        }

        serializer_data = CMSPageSerializer().to_representation(page, use_fake=True)
        self.assertDictEqual(serializer_data['fields'][0], {
            'name': 'a',
            'type': 'string',
            'value': 'b'
        })
        self.assertDictEqual(serializer_data['meta']['b'], {
            'name': 'b',
            'type': 'string',
            'value': 'c'
        })
