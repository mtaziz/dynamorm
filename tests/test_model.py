import os
import pytest

from dynamorm.model import DynaModel
from dynamorm.exceptions import InvalidSchemaField, MissingTableAttribute, DynaModelException
if 'marshmallow' in (os.getenv('SERIALIZATION_PKG') or ''):
    from marshmallow.fields import String
    from marshmallow.fields import Number
else:
    from schematics.types import StringType as String
    from schematics.types import IntType as Number


def test_missing_inner_classes():
    """Classes must have both a Table and Schema inner class"""
    with pytest.raises(DynaModelException):
        class Model(DynaModel):
            pass


def test_missing_inner_schema_class():
    """Classes must have an inner Schema class"""
    with pytest.raises(DynaModelException):
        class Model(DynaModel):
            class Table:
                pass


def test_missing_inner_table_class():
    """Classes must have an inner Table class"""
    with pytest.raises(DynaModelException):
        class Model(DynaModel):
            class Schema:
                pass


def test_parent_inner_classes():
    class Parent(DynaModel):
        class Table:
            name = 'table'
            hash_key = 'foo'
            read = 1
            write = 1

        class Schema:
            foo = String(required=True)

    class Child(Parent):
        pass

    assert Child.Table is Parent.Table


def test_table_validation():
    """Defining a model with missing table attributes should raise exceptions"""
    with pytest.raises(MissingTableAttribute):
        class Model(DynaModel):
            class Table:
                name = 'table'

            class Schema:
                foo = String(required=True)


def test_table_create_validation():
    """You cannot create a table that is missing read/write attrs"""
    with pytest.raises(MissingTableAttribute):
        class Model(DynaModel):
            class Table:
                name = 'table'
                hash_key = 'foo'
                read = 5

            class Schema:
                foo = String(required=True)

        Model.Table.create()

    with pytest.raises(MissingTableAttribute):
        class Model(DynaModel):
            class Table:
                name = 'table'
                hash_key = 'foo'
                write = 5

            class Schema:
                foo = String(required=True)

        Model.Table.create()

    with pytest.raises(MissingTableAttribute):
        class Model(DynaModel):
            class Table:
                name = 'table'
                hash_key = 'foo'

            class Schema:
                foo = String(required=True)

        Model.Table.create()


def test_invalid_hash_key():
    """Defining a model where ``hash_key`` in Table points to an invalid field should raise InvalidSchemaField"""
    with pytest.raises(InvalidSchemaField):
        class Model(DynaModel):
            class Table:
                name = 'table'
                hash_key = 'foo'
                read = 1
                write = 1

            class Schema:
                bar = String(required=True)


def test_invalid_range_key():
    """Defining a model where ``range_key`` in Table points to an invalid field should raise InvalidSchemaField"""
    with pytest.raises(InvalidSchemaField):
        class Model(DynaModel):
            class Table:
                name = 'table'
                hash_key = 'foo'
                range_key = 'bar'
                read = 1
                write = 1

            class Schema:
                foo = String(required=True)
                baz = String(required=True)


def test_number_hash_key():
    """Test a number hash key and ensure the dynamo type gets set correctly"""
    class Model(DynaModel):
        class Table:
            name = 'table'
            hash_key = 'foo'
            read = 1
            write = 1

        class Schema:
            foo = Number(required=True)
            baz = String(required=True)

    model = Model(foo=1, baz='foo')
    assert model.Table.attribute_definitions == [{'AttributeName': 'foo', 'AttributeType': 'N'}]
