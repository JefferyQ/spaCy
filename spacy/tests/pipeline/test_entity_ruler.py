# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Span
from spacy.language import Language
from spacy.pipeline import EntityRuler


@pytest.fixture
def nlp():
    return Language()


@pytest.fixture
def patterns():
    return [
        {"label": "HELLO", "pattern": "hello world"},
        {"label": "BYE", "pattern": [{"LOWER": "bye"}, {"LOWER": "bye"}]},
        {"label": "HELLO", "pattern": [{"ORTH": "HELLO"}]},
        {"label": "COMPLEX", "pattern": [{"ORTH": "foo", "OP": "*"}]},
        {"label": "TECH_ORG", "pattern": "Apple", "id": "a1"},
    ]


@pytest.fixture
def add_ent():
    def add_ent_component(doc):
        doc.ents = [Span(doc, 0, 3, label=doc.vocab.strings["ORG"])]
        return doc

    return add_ent_component


def test_entity_ruler_init(nlp, patterns):
    ruler = EntityRuler(nlp, patterns=patterns)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    assert "HELLO" in ruler
    assert "BYE" in ruler
    nlp.add_pipe(ruler)
    doc = nlp("hello world bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "HELLO"
    assert doc.ents[1].label_ == "BYE"


def test_entity_ruler_existing(nlp, patterns, add_ent):
    ruler = EntityRuler(nlp, patterns=patterns)
    nlp.add_pipe(add_ent)
    nlp.add_pipe(ruler)
    doc = nlp("OH HELLO WORLD bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "ORG"
    assert doc.ents[1].label_ == "BYE"


def test_entity_ruler_existing_overwrite(nlp, patterns, add_ent):
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    nlp.add_pipe(add_ent)
    nlp.add_pipe(ruler)
    doc = nlp("OH HELLO WORLD bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "HELLO"
    assert doc.ents[0].text == "HELLO"
    assert doc.ents[1].label_ == "BYE"


def test_entity_ruler_existing_complex(nlp, patterns, add_ent):
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    nlp.add_pipe(add_ent)
    nlp.add_pipe(ruler)
    doc = nlp("foo foo bye bye")
    assert len(doc.ents) == 2
    assert doc.ents[0].label_ == "COMPLEX"
    assert doc.ents[1].label_ == "BYE"
    assert len(doc.ents[0]) == 2
    assert len(doc.ents[1]) == 2


def test_entity_ruler_entity_id(nlp, patterns):
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True)
    nlp.add_pipe(ruler)
    doc = nlp("Apple is a technology company")
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "TECH_ORG"
    assert doc.ents[0].ent_id_ == "a1"


def test_entity_ruler_cfg_ent_id_sep(nlp, patterns):
    ruler = EntityRuler(nlp, patterns=patterns, overwrite_ents=True, ent_id_sep="**")
    assert "TECH_ORG**a1" in ruler.phrase_patterns
    nlp.add_pipe(ruler)
    doc = nlp("Apple is a technology company")
    assert len(doc.ents) == 1
    assert doc.ents[0].label_ == "TECH_ORG"
    assert doc.ents[0].ent_id_ == "a1"


def test_entity_ruler_serialize_bytes(nlp, patterns):
    ruler = EntityRuler(nlp, patterns=patterns)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
    ruler_bytes = ruler.to_bytes()
    new_ruler = EntityRuler(nlp)
    assert len(new_ruler) == 0
    assert len(new_ruler.labels) == 0
    new_ruler = new_ruler.from_bytes(ruler_bytes)
    assert len(ruler) == len(patterns)
    assert len(ruler.labels) == 4
