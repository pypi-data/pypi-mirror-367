"""
Syllabify main module
Updated to Python 3 from Python 2 original
"""

import re
import copy
import sys
import random
import functools
from .cmu_parser import CMUtranscribe
from .syllable_types import Cluster, Consonant, Vowel, Empty, Rime, Syllable, Word
from .phoneme_types import *
from typing import List

phoneme_classify = re.compile(
    r"""
                        ((?P<Vowel>AO|UW|EH|AH|AA|IY|IH|UH|AE|AW|AY|ER|EY|OW|OY)
                        |(?P<Consonant>CH|DH|HH|JH|NG|SH|TH|ZH|Z|S|P|R|K|L|M|N|F|G|D|B|T|V|W|Y\d*)
                        )
                        ((?P<Stress>0|1|2)
                        )?
                        """,
    re.VERBOSE,
)


def factory(phoneme):
    """argument is a string of phonemes e.g.'B IH0 K AH0 Z'"""
    phoneme_list = phoneme.split()

    def phoneme_fact(phoneme):
        # match against regular expression
        phoneme_feature = re.match(phoneme_classify, phoneme).groupdict()

        # input is phoneme feature dictionary
        if phoneme_feature["Consonant"]:
            # return consonant object
            return Consonant(**phoneme_feature)
        elif phoneme_feature["Vowel"]:
            # return vowel object
            return Vowel(**phoneme_feature)
        else:
            # unknown phoneme class
            raise Exception(
                "unknown Phoneme Class: cannot create appropriate Phoneme object"
            )

    def cluster_fact(cluster_list, phoneme):
        current_cluster = cluster_list.pop()

        # Consonants must be grouped together into clusters
        if (
            current_cluster.type() == Consonant
            and type(phoneme) == Consonant
            or current_cluster.type() is None
        ):
            # Adjacent phonemes of type consonant belong to the same cluster, if the
            # current cluster.last_phoneme == None that means it's empty
            # update current cluster
            # AC 2017-08-12: provided it's not NG (should not be clustered)
            if NG in current_cluster.get_phoneme_string():
                # create new cluster add phoneme to it and return
                cluster_list.append(current_cluster)
                cluster_list.append(Cluster(phoneme))
            else:
                current_cluster.add_phoneme(phoneme)
                # append to cluster list
                cluster_list.append(current_cluster)
            # return cluster list
            return cluster_list
        else:
            # create new cluster add phoneme to it and return
            cluster_list.append(current_cluster)
            cluster_list.append(Cluster(phoneme))
            return cluster_list

    def syllable_fact(syllable_list, cluster):
        syllable = syllable_list.pop()
        push = syllable_list.append

        if (
            syllable.onset_is_empty()
            and syllable.nucleus_is_empty()
            and cluster.type() == Consonant
        ):
            # cluster is assigned to the onset of the current syllable
            syllable.set_onset(cluster)
            push(syllable)
            return syllable_list

        if cluster.type() == Vowel:
            if syllable.has_nucleus():
                # this cluster becomes the nucleus of a new syllable
                # push current syllable back on the syllable stack
                push(syllable)
                # create new syllable
                new_syllable = Syllable(nucleus=cluster)
                # push new_syllable onto the stack
                push(new_syllable)
                return syllable_list
            else:
                # syllable does not have nucleus so this cluster becomes the
                # nucleus on the current syllable
                syllable.set_nucleus(cluster)
                push(syllable)
                return syllable_list

        if syllable.has_nucleus() and cluster.type() == Consonant:
            if syllable.has_coda():
                # this cluster is the onset of the next syllable
                new_syllable = Syllable(onset=cluster)
                # push syllable onto stack
                push(new_syllable)
                return syllable_list
            elif syllable.coda_is_empty():
                # Onset Maximalism dictates we push consonant clusters to
                # the onset of the next syllable, unless the nuclear cluster is LIGHT and
                # has primary stress
                maximal_coda, maximal_onset = onset_rules(cluster)

                # AC 2017-09-15: removed ambisyllabicity as a theoretical stance
                # add cluster only to the next syllable
                if maximal_coda:
                    syllable.set_coda(maximal_coda)
                    push(syllable)
                else:
                    push(syllable)
                if maximal_onset:
                    new_syllable = Syllable(onset=maximal_onset)
                else:
                    new_syllable = Syllable()
                push(new_syllable)
                return syllable_list

    def check_last_syllable(syllable_list):
        # the syllable algorithm may assign a consonant cluster to a syllable that does not have
        # a nucleus, this is not allowed in the English language.

        # check the last syllable
        syllable = syllable_list.pop()
        push = syllable_list.append

        if syllable.nucleus_is_empty():
            if syllable.has_onset():
                # pop the previous syllable
                prev_syllable = syllable_list.pop()
                onset = syllable.get_onset()
                # set the coda of the previous syllable to the value of the orphan onset
                if prev_syllable.has_coda():
                    # add phoneme
                    coda_cluster = prev_syllable.get_coda()
                    if coda_cluster != onset:
                        for phoneme in onset.phoneme_list:
                            coda_cluster.add_phoneme(phoneme)
                        push(prev_syllable)
                    else:
                        push(prev_syllable)
                else:
                    prev_syllable.set_coda(onset)
                    push(prev_syllable)
        else:
            # There is no violation, push syllable back on the stack
            push(syllable)

        return syllable_list

    # Create a list of phoneme clusters from phoneme list
    cluster_list = functools.reduce(
        cluster_fact, map(phoneme_fact, phoneme_list), [Cluster()]
    )

    # Apply syllable creation rules to list of phoneme clusters
    syllable_list = functools.reduce(syllable_fact, cluster_list, [Syllable()])

    # Validate last syllable, and return completed syllable list
    return check_last_syllable(syllable_list)


def coda_rules(cluster):
    """checks if the cluster is a valid onset or whether it needs to be split"""

    coda_cluster = copy.deepcopy(cluster)
    phonemes = map(str, coda_cluster.get_phoneme())
    phonemelist = list(
        phonemes
    )  # grabbed list of phonemes to move away from Py3 map problem, and strip trailing spaces
    list_of_phonemes = []
    for phone in phonemelist:
        list_of_phonemes.append(phone.rstrip())

    def _split_and_update(
        phoneme, phonemes=list_of_phonemes, coda_cluster=coda_cluster
    ):
        index = phonemes.index(phoneme)
        # split on phoneme and discard the rest
        head = coda_cluster.phoneme_list[: index - 1]
        # update cluster
        coda_cluster.phoneme_list = head
        # update string list
        phonemes = phonemes[: index - 1]

        return (phonemes, coda_cluster)

    # rule 1 - no /HH/ in coda
    if HH in list_of_phonemes:
        list_of_phonemes, coda_cluster = _split_and_update("HH")

    # rule 2 - no glides in coda
    # if L in list_of_phonemes:  # commented out by AC
    #     list_of_phonemes, coda_cluster = _split_and_update('L')

    # if R in list_of_phonemes:  # commented out by AC
    #     list_of_phonemes, coda_cluster = _split_and_update('R')

    if W in list_of_phonemes:
        list_of_phonemes, coda_cluster = _split_and_update("W")

    if Y in list_of_phonemes:
        list_of_phonemes, coda_cluster = _split_and_update("Y")

    # rule 3 - if complex coda second consonant must not be
    # /NG/ /ZH/ /DH/
    if len(list_of_phonemes) > 1 and list_of_phonemes[1] in [NG, DH, ZH]:
        phoneme = coda_cluster.phoneme_list[1]
        # update cluster
        coda_cluster.phoneme_list = [phoneme]
        # update string list
        phonemes = list_of_phonemes[0:1]

    if coda_cluster.phoneme_list == []:
        coda_cluster = None

    return coda_cluster

def onset_rules(cluster):
    """checks if the cluster is a valid onset or whether it needs to be split"""

    phonemes = map(str, cluster.get_phoneme())
    phonemelist = list(
        phonemes
    )  # grabbed list of phonemes to move away from Py3 map problem, and strip trailing spaces
    list_of_phonemes = []
    for phone in phonemelist:
        list_of_phonemes.append(phone.rstrip())
    coda_cluster = Cluster()

    def _split_and_update(
        phoneme, phonemes=list_of_phonemes, coda_cluster=coda_cluster
    ):
        # get index of phoneme
        index = phonemes.index(phoneme)
        # split on phoneme and add tail coda cluster
        tail = cluster.phoneme_list[:index]
        # remaining phonemes
        head = cluster.phoneme_list[index:]
        # extend list
        coda_cluster.phoneme_list.extend(tail)
        # update cluster
        cluster.phoneme_list = head
        # update string list
        phonemes = phonemes[index:]
        return (phonemes, coda_cluster)

    def _remove_and_update(phonemes=list_of_phonemes, coda_cluster=coda_cluster):
        head = cluster.phoneme_list[0]
        rest = cluster.phoneme_list[1:]
        # extend list
        coda_cluster.phoneme_list.extend([head])
        # update cluster
        cluster.phoneme_list = rest
        # update string list
        phonemes = phonemes[1:]
        return (phonemes, coda_cluster)

    # rule 1 - /NG/ cannot exist in a valid onset
    # does /NG? exist? split on NG add NG to coda
    if NG in list_of_phonemes:
        list_of_phonemes, coda_cluster = _remove_and_update()

    # rule 2a - no affricates in complex onsets
    # /CH/ exist? split on affricate
    if CH in list_of_phonemes:
        list_of_phonemes, coda_cluster = _split_and_update("CH")

    # rule 2b - no affricates in complex onsets
    # /JH/ exist? split on affricate
    if JH in list_of_phonemes:
        list_of_phonemes, coda_cluster = _split_and_update("JH")

    # rule 3 - first consonant in a complex onset must be obstruent
    # if first consonant stop or fricative or nasal
    if len(list_of_phonemes) > 1 and not list_of_phonemes[0] in [
        B,
        D,
        G,
        K,
        P,
        T,
        DH,
        F,
        S,
        SH,
        TH,
        V,
        ZH,
        M,
        N,
    ]:
        list_of_phonemes, coda_cluster = _remove_and_update()

    # rule 4 - second consonant in a complex onset must be a voiced obstruent
    # if not OBSTRUENT and VOICED? split on second consonant
    if (
        len(list_of_phonemes) > 1
        and not list_of_phonemes[0] == S
        and not list_of_phonemes[1] in [B, M, V, D, N, Z, ZH, R, Y]
    ):
        list_of_phonemes, coda_cluster = _remove_and_update()

    # rule 5 - if first consonant in a complex onset is not /s/
    # the second consonant must be liquid or glide /L/ /R/ /W/ /Y/
    if (
        len(list_of_phonemes) > 1
        and not list_of_phonemes[0] == S
        and not list_of_phonemes[1] in [L, R, W, Y]
        and len(list_of_phonemes) < 3
    ):
        list_of_phonemes, coda_cluster = _remove_and_update()

    # rule 6 - deal with N|DR, ND|L, T|BR clusters
    if (
        len(list_of_phonemes) > 2
        and list_of_phonemes[0] in ["N", "T", "TH"]
        and list_of_phonemes[1] in ["D", "B"]
    ):
        if (
            list_of_phonemes[0] in ["R", "T"]
            and list_of_phonemes[1] in ["B"]
            and list_of_phonemes[2] in ["R"]
        ):  # heartbreak
            list_of_phonemes, coda_cluster = _split_and_update(list_of_phonemes[0])
        elif list_of_phonemes[0] in ["TH"]:  # toothbrush
            list_of_phonemes, coda_cluster = _split_and_update(list_of_phonemes[1])
        elif list_of_phonemes[0] in ["N"] or list_of_phonemes[2] in ["L", "M"]:
            if list_of_phonemes[1] in ["D"] and list_of_phonemes[2] in ["R"]:  # undress
                list_of_phonemes, coda_cluster = _split_and_update(list_of_phonemes[1])
            else:  # endless, handbag
                list_of_phonemes, coda_cluster = _split_and_update(list_of_phonemes[2])

    if coda_cluster.get_phoneme() == []:
        coda_cluster = None

    if cluster.get_phoneme() == []:
        cluster = None

    return (coda_cluster, cluster)


def generate(word):
    """Generate syllables from a word using the CMU Pronouncing Dictionary"""
    phoneme_list = CMUtranscribe(word.strip())
    if phoneme_list:
        return factory(phoneme_list[0])  # first version only
    else:
        print(word + " not in CMU dictionary, sorry, please try again...")
        return None

# generate syllables from a sentence
def generate_sentence(sentence: str) -> List[Word]:
    """Generate syllables from a sentence using the CMU Pronouncing Dictionary"""
    words = sentence.split()
    word_objects = []
    for word in words:
        syllables = generate(word.rstrip())
        if syllables:
            word_objects.append(Word(syllables))
    return word_objects

def get_raw(word):
    """Get raw phoneme transcription"""
    return CMUtranscribe(word)
