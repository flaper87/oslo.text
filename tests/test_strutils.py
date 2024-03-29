# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_text
----------------------------------

Tests for `text` module.
"""
import math

import mock
from oslotest import base as test_base
import six
import testscenarios

from oslo.text import strutils

load_tests = testscenarios.load_tests_apply_scenarios


class StrUtilsTest(test_base.BaseTestCase):

    def test_bool_bool_from_string(self):
        self.assertTrue(strutils.bool_from_string(True))
        self.assertFalse(strutils.bool_from_string(False))

    def test_bool_bool_from_string_default(self):
        self.assertTrue(strutils.bool_from_string('', default=True))
        self.assertFalse(strutils.bool_from_string('wibble', default=False))

    def _test_bool_from_string(self, c):
        self.assertTrue(strutils.bool_from_string(c('true')))
        self.assertTrue(strutils.bool_from_string(c('TRUE')))
        self.assertTrue(strutils.bool_from_string(c('on')))
        self.assertTrue(strutils.bool_from_string(c('On')))
        self.assertTrue(strutils.bool_from_string(c('yes')))
        self.assertTrue(strutils.bool_from_string(c('YES')))
        self.assertTrue(strutils.bool_from_string(c('yEs')))
        self.assertTrue(strutils.bool_from_string(c('1')))
        self.assertTrue(strutils.bool_from_string(c('T')))
        self.assertTrue(strutils.bool_from_string(c('t')))
        self.assertTrue(strutils.bool_from_string(c('Y')))
        self.assertTrue(strutils.bool_from_string(c('y')))

        self.assertFalse(strutils.bool_from_string(c('false')))
        self.assertFalse(strutils.bool_from_string(c('FALSE')))
        self.assertFalse(strutils.bool_from_string(c('off')))
        self.assertFalse(strutils.bool_from_string(c('OFF')))
        self.assertFalse(strutils.bool_from_string(c('no')))
        self.assertFalse(strutils.bool_from_string(c('0')))
        self.assertFalse(strutils.bool_from_string(c('42')))
        self.assertFalse(strutils.bool_from_string(c(
                         'This should not be True')))
        self.assertFalse(strutils.bool_from_string(c('F')))
        self.assertFalse(strutils.bool_from_string(c('f')))
        self.assertFalse(strutils.bool_from_string(c('N')))
        self.assertFalse(strutils.bool_from_string(c('n')))

        # Whitespace should be stripped
        self.assertTrue(strutils.bool_from_string(c(' 1 ')))
        self.assertTrue(strutils.bool_from_string(c(' true ')))
        self.assertFalse(strutils.bool_from_string(c(' 0 ')))
        self.assertFalse(strutils.bool_from_string(c(' false ')))

    def test_bool_from_string(self):
        self._test_bool_from_string(lambda s: s)

    def test_unicode_bool_from_string(self):
        self._test_bool_from_string(six.text_type)
        self.assertFalse(strutils.bool_from_string(u'使用', strict=False))

        exc = self.assertRaises(ValueError, strutils.bool_from_string,
                                u'使用', strict=True)
        expected_msg = (u"Unrecognized value '使用', acceptable values are:"
                        u" '0', '1', 'f', 'false', 'n', 'no', 'off', 'on',"
                        u" 't', 'true', 'y', 'yes'")
        self.assertEqual(expected_msg, six.text_type(exc))

    def test_other_bool_from_string(self):
        self.assertFalse(strutils.bool_from_string(None))
        self.assertFalse(strutils.bool_from_string(mock.Mock()))

    def test_int_bool_from_string(self):
        self.assertTrue(strutils.bool_from_string(1))

        self.assertFalse(strutils.bool_from_string(-1))
        self.assertFalse(strutils.bool_from_string(0))
        self.assertFalse(strutils.bool_from_string(2))

    def test_strict_bool_from_string(self):
        # None isn't allowed in strict mode
        exc = self.assertRaises(ValueError, strutils.bool_from_string, None,
                                strict=True)
        expected_msg = ("Unrecognized value 'None', acceptable values are:"
                        " '0', '1', 'f', 'false', 'n', 'no', 'off', 'on',"
                        " 't', 'true', 'y', 'yes'")
        self.assertEqual(expected_msg, str(exc))

        # Unrecognized strings aren't allowed
        self.assertFalse(strutils.bool_from_string('Other', strict=False))
        exc = self.assertRaises(ValueError, strutils.bool_from_string, 'Other',
                                strict=True)
        expected_msg = ("Unrecognized value 'Other', acceptable values are:"
                        " '0', '1', 'f', 'false', 'n', 'no', 'off', 'on',"
                        " 't', 'true', 'y', 'yes'")
        self.assertEqual(expected_msg, str(exc))

        # Unrecognized numbers aren't allowed
        exc = self.assertRaises(ValueError, strutils.bool_from_string, 2,
                                strict=True)
        expected_msg = ("Unrecognized value '2', acceptable values are:"
                        " '0', '1', 'f', 'false', 'n', 'no', 'off', 'on',"
                        " 't', 'true', 'y', 'yes'")
        self.assertEqual(expected_msg, str(exc))

        # False-like values are allowed
        self.assertFalse(strutils.bool_from_string('f', strict=True))
        self.assertFalse(strutils.bool_from_string('false', strict=True))
        self.assertFalse(strutils.bool_from_string('off', strict=True))
        self.assertFalse(strutils.bool_from_string('n', strict=True))
        self.assertFalse(strutils.bool_from_string('no', strict=True))
        self.assertFalse(strutils.bool_from_string('0', strict=True))

        self.assertTrue(strutils.bool_from_string('1', strict=True))

        # Avoid font-similarity issues (one looks like lowercase-el, zero like
        # oh, etc...)
        for char in ('O', 'o', 'L', 'l', 'I', 'i'):
            self.assertRaises(ValueError, strutils.bool_from_string, char,
                              strict=True)

    def test_int_from_bool_as_string(self):
        self.assertEqual(1, strutils.int_from_bool_as_string(True))
        self.assertEqual(0, strutils.int_from_bool_as_string(False))

    def test_safe_decode(self):
        safe_decode = strutils.safe_decode
        self.assertRaises(TypeError, safe_decode, True)
        self.assertEqual(six.u('ni\xf1o'), safe_decode(six.b("ni\xc3\xb1o"),
                         incoming="utf-8"))
        if six.PY2:
            # In Python 3, bytes.decode() doesn't support anymore
            # bytes => bytes encodings like base64
            self.assertEqual(six.u("test"), safe_decode("dGVzdA==",
                             incoming='base64'))

        self.assertEqual(six.u("strange"), safe_decode(six.b('\x80strange'),
                         errors='ignore'))

        self.assertEqual(six.u('\xc0'), safe_decode(six.b('\xc0'),
                         incoming='iso-8859-1'))

        # Forcing incoming to ascii so it falls back to utf-8
        self.assertEqual(six.u('ni\xf1o'), safe_decode(six.b('ni\xc3\xb1o'),
                         incoming='ascii'))

        self.assertEqual(six.u('foo'), safe_decode(b'foo'))

    def test_safe_encode(self):
        safe_encode = strutils.safe_encode
        self.assertRaises(TypeError, safe_encode, True)
        self.assertEqual(six.b("ni\xc3\xb1o"), safe_encode(six.u('ni\xf1o'),
                                                           encoding="utf-8"))
        if six.PY2:
            # In Python 3, str.encode() doesn't support anymore
            # text => text encodings like base64
            self.assertEqual(six.b("dGVzdA==\n"),
                             safe_encode("test", encoding='base64'))
        self.assertEqual(six.b('ni\xf1o'), safe_encode(six.b("ni\xc3\xb1o"),
                                                       encoding="iso-8859-1",
                                                       incoming="utf-8"))

        # Forcing incoming to ascii so it falls back to utf-8
        self.assertEqual(six.b('ni\xc3\xb1o'),
                         safe_encode(six.b('ni\xc3\xb1o'), incoming='ascii'))
        self.assertEqual(six.b('foo'), safe_encode(six.u('foo')))

    def test_slugify(self):
        to_slug = strutils.to_slug
        self.assertRaises(TypeError, to_slug, True)
        self.assertEqual(six.u("hello"), to_slug("hello"))
        self.assertEqual(six.u("two-words"), to_slug("Two Words"))
        self.assertEqual(six.u("ma-any-spa-ce-es"),
                         to_slug("Ma-any\t spa--ce- es"))
        self.assertEqual(six.u("excamation"), to_slug("exc!amation!"))
        self.assertEqual(six.u("ampserand"), to_slug("&ampser$and"))
        self.assertEqual(six.u("ju5tnum8er"), to_slug("ju5tnum8er"))
        self.assertEqual(six.u("strip-"), to_slug(" strip - "))
        self.assertEqual(six.u("perche"), to_slug(six.b("perch\xc3\xa9")))
        self.assertEqual(six.u("strange"),
                         to_slug("\x80strange", errors="ignore"))


class StringToBytesTest(test_base.BaseTestCase):

    _unit_system = [
        ('si', dict(unit_system='SI')),
        ('iec', dict(unit_system='IEC')),
        ('invalid_unit_system', dict(unit_system='KKK', assert_error=True)),
        ('invalid_sign', dict(sign='~', assert_error=True)),
    ]

    _sign = [
        ('no_sign', dict(sign='')),
        ('positive', dict(sign='+')),
        ('negative', dict(sign='-')),
        ('invalid_sign', dict(sign='~', assert_error=True)),
    ]

    _magnitude = [
        ('integer', dict(magnitude='79')),
        ('decimal', dict(magnitude='7.9')),
        ('decimal_point_start', dict(magnitude='.9')),
        ('decimal_point_end', dict(magnitude='79.', assert_error=True)),
        ('invalid_literal', dict(magnitude='7.9.9', assert_error=True)),
        ('garbage_value', dict(magnitude='asdf', assert_error=True)),
    ]

    _unit_prefix = [
        ('no_unit_prefix', dict(unit_prefix='')),
        ('k', dict(unit_prefix='k')),
        ('K', dict(unit_prefix='K')),
        ('M', dict(unit_prefix='M')),
        ('G', dict(unit_prefix='G')),
        ('T', dict(unit_prefix='T')),
        ('Ki', dict(unit_prefix='Ki')),
        ('Mi', dict(unit_prefix='Mi')),
        ('Gi', dict(unit_prefix='Gi')),
        ('Ti', dict(unit_prefix='Ti')),
        ('invalid_unit_prefix', dict(unit_prefix='B', assert_error=True)),
    ]

    _unit_suffix = [
        ('b', dict(unit_suffix='b')),
        ('bit', dict(unit_suffix='bit')),
        ('B', dict(unit_suffix='B')),
        ('invalid_unit_suffix', dict(unit_suffix='Kg', assert_error=True)),
    ]

    _return_int = [
        ('return_dec', dict(return_int=False)),
        ('return_int', dict(return_int=True)),
    ]

    @classmethod
    def generate_scenarios(cls):
        cls.scenarios = testscenarios.multiply_scenarios(cls._unit_system,
                                                         cls._sign,
                                                         cls._magnitude,
                                                         cls._unit_prefix,
                                                         cls._unit_suffix,
                                                         cls._return_int)

    def test_string_to_bytes(self):

        def _get_quantity(sign, magnitude, unit_suffix):
            res = float('%s%s' % (sign, magnitude))
            if unit_suffix in ['b', 'bit']:
                res /= 8
            return res

        def _get_constant(unit_prefix, unit_system):
            if not unit_prefix:
                return 1
            elif unit_system == 'SI':
                res = getattr(units, unit_prefix)
            elif unit_system == 'IEC':
                if unit_prefix.endswith('i'):
                    res = getattr(units, unit_prefix)
                else:
                    res = getattr(units, '%si' % unit_prefix)
            return res

        text = ''.join([self.sign, self.magnitude, self.unit_prefix,
                        self.unit_suffix])
        err_si = self.unit_system == 'SI' and (self.unit_prefix == 'K' or
                                               self.unit_prefix.endswith('i'))
        err_iec = self.unit_system == 'IEC' and self.unit_prefix == 'k'
        if getattr(self, 'assert_error', False) or err_si or err_iec:
            self.assertRaises(ValueError, strutils.string_to_bytes,
                              text, unit_system=self.unit_system,
                              return_int=self.return_int)
            return
        quantity = _get_quantity(self.sign, self.magnitude, self.unit_suffix)
        constant = _get_constant(self.unit_prefix, self.unit_system)
        expected = quantity * constant
        actual = strutils.string_to_bytes(text, unit_system=self.unit_system,
                                          return_int=self.return_int)
        if self.return_int:
            self.assertEqual(actual, int(math.ceil(expected)))
        else:
            self.assertAlmostEqual(actual, expected)

StringToBytesTest.generate_scenarios()
