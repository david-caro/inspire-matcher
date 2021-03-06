# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import pytest

from inspire_matcher.core import _compile_exact, _compile_nested


def test_compile_exact():
    query = {
        'path': 'arxiv_eprints.value',
        'search_path': 'arxiv_eprints.value.raw',
        'type': 'exact',
    }
    record = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th',
                ],
                'value': 'hep-th/9711200',
            },
        ],
    }

    expected = {
        'query': {
            'bool': {
                'should': [
                    {
                        'match': {
                            'arxiv_eprints.value.raw': 'hep-th/9711200',
                        },
                    },
                ],
            },
        },
    }
    result = _compile_exact(query, record)

    assert expected == result


def test_compile_exact_supports_a_collection():
    query = {
        'collections': [
            'HAL Hidden',
        ],
        'path': 'arxiv_eprints.value',
        'search_path': 'arxiv_eprints.value.raw',
        'type': 'exact',
    }
    record = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th',
                ],
                'value': 'hep-th/9711200',
            },
        ],
    }

    expected = {
        'query': {
            'bool': {
                'minimum_should_match': 1,
                'filter': {
                    'bool': {
                        'should': [
                            {
                                'match': {
                                    '_collections': 'HAL Hidden',
                                },
                            },
                        ],
                    },
                },
                'should': [
                    {
                        'match': {
                            'arxiv_eprints.value.raw': 'hep-th/9711200',
                        },
                    },
                ],
            },
        },
    }
    result = _compile_exact(query, record)

    assert expected == result


def test_compile_exact_supports_multiple_collections():
    query = {
        'collections': [
            'CDS Hidden',
            'HAL Hidden',
        ],
        'path': 'arxiv_eprints.value',
        'search_path': 'arxiv_eprints.value.raw',
        'type': 'exact',
    }
    record = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th',
                ],
                'value': 'hep-th/9711200',
            },
        ],
    }

    expected = {
        'query': {
            'bool': {
                'minimum_should_match': 1,
                'filter': {
                    'bool': {
                        'should': [
                            {
                                'match': {
                                    '_collections': 'CDS Hidden',
                                },
                            },
                            {
                                'match': {
                                    '_collections': 'HAL Hidden',
                                },
                            },
                        ],
                    },
                },
                'should': [
                    {
                        'match': {
                            'arxiv_eprints.value.raw': 'hep-th/9711200',
                        },
                    },
                ],
            },
        },
    }
    result = _compile_exact(query, record)

    assert expected == result


def test_compile_exact_supports_non_list_fields():
    query = {
        'path': 'reference.arxiv_eprint',
        'search_path': 'arxiv_eprints.value.raw',
        'type': 'exact',
    }
    reference = {
        'reference': {
            'arxiv_eprint': 'hep-th/9711200',
        },
    }

    expected = {
        'query': {
            'bool': {
                'should': [
                    {
                        'match': {
                            'arxiv_eprints.value.raw': 'hep-th/9711200',
                        },
                    },
                ],
            },
        },
    }
    result = _compile_exact(query, reference)

    assert expected == result


def test_compile_nested():
    query = {
        'paths': [
            'reference.publication_info.journal_title',
            'reference.publication_info.journal_volume',
            'reference.publication_info.artid',
        ],
        'search_paths': [
            'publication_info.journal_title',
            'publication_info.journal_volume',
            'publication_info.artid',
        ],
        'type': 'nested',
    }
    reference = {
        'reference': {
            'publication_info': {
                'journal_title': 'Phys.Rev.',
                'journal_volume': 'D94',
                'artid': '124054',
            },
        },
    }

    expected = {
        'query': {
            'nested': {
                'path': 'publication_info',
                'query': {
                    'bool': {
                        'must': [
                            {
                                'match': {
                                    'publication_info.journal_title': 'Phys.Rev.',
                                },
                            },
                            {
                                'match': {
                                    'publication_info.journal_volume': 'D94',
                                },
                            },
                            {
                                'match': {
                                    'publication_info.artid': '124054',
                                },
                            },
                        ],
                    },
                },
            },
        },
    }
    result = _compile_nested(query, reference)

    assert expected == result


def test_compile_nested_requires_all_paths_to_contain_a_value_in_order_to_generate_a_query():
    query = {
        'paths': [
            'reference.publication_info.journal_title',
            'reference.publication_info.journal_volume',
            'reference.publication_info.artid',
        ],
        'search_paths': [
            'publication_info.journal_title',
            'publication_info.journal_volume',
            'publication_info.artid',
        ],
    }
    reference = {
        'reference': {
            'publication_info': {
                'label': '23',
                'misc': [
                    'Strai~burger, C., this Conference',
                ],
            },
        },
    }

    assert _compile_nested(query, reference) is None


def test_compile_nested_raises_when_search_paths_dont_share_a_common_path():
    query = {
        'paths': [
            'foo.bar',
            'foo.baz',
        ],
        'search_paths': [
            'bar',
            'baz',
        ],
        'type': 'nested',
    }

    with pytest.raises(ValueError) as excinfo:
        _compile_nested(query, None)
    assert 'common path' in str(excinfo.value)


def test_compile_nested_raises_when_paths_and_search_paths_dont_have_the_same_length():
    query = {
        'paths': [
            'foo',
            'bar',
        ],
        'search_paths': [
            'baz'
        ],
        'type': 'nested',
    }

    with pytest.raises(ValueError) as excinfo:
        _compile_nested(query, None)
    assert 'same length' in str(excinfo.value)
