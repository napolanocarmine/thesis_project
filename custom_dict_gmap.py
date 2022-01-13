from implicit_dict_v2 import implicit_dict
from pixel_map_z_curve_full import D, plot

from collections import defaultdict
from itertools import chain, product
import logging

class dict_nGmap:
    
    def __init__(self, n, set_darts=None):
        
        self.n = n

        """
            A simple instance of the implicit_dict class.
        """
        self.impl_dict = implicit_dict()
        
        """
            Initialization of the set of darts obtained from the implicitly encoding -> Morton code.
        """
        if set_darts == None:
            self.darts = D
        else:
            self.darts = set_darts
        #print(self.darts)

        """
            Initialization of custom python dictionaries to handle the involutions of the n-Gmap during the use
            of the Morton code as implicitly encoding. Each alpha represent the ACTIVE part of the data structure,
            i.e., the current n-Gmap.
        """
        self.alpha = [implicit_dict(i) for i in range(n + 1)]

        #self.print_alpha()

        self.marks = defaultdict(lambda:defaultdict(lambda:False))
        # self.marks[index][dart]
        
        """
            Added a tmp dict to create a tmp-Gmap to insert/expand it into the current one.
        """
        self.c = {}


        """
            That variable has the goal of increment itself whenever a new operation is computed
            (removal or contraction).
        """
        self.level = 0

        """
            I want to use the following dictionary to keep trace of the level for each dart in order
            to reconstruct also until a certain level that the user can indicate in input.
        """
        self.dart_level = {}

        """
            Considering the idea behind the implementation, I need to have the PASSIVE part
            according to the canonical encoding. It is represented by the custom alphas.
        """
        self.custom_alpha = [dict() for _ in range(n + 1)]
        
        self.taken_marks = {-1}
        self.lowest_unused_dart_index = 0
        
    @classmethod
    def from_string(cls, string):
        lines = string.strip().split("\n")
        lines = [[int(k) for k in l.split(" ") if k != ""] for l in lines]
    
        return cls.from_list_of_lists(lines)
        
    @classmethod    
    def from_list_of_lists(cls, ll):
        n = len(ll) - 1
        d = len(ll[0])
        
        darts = set(ll[0])
        
        assert all(set(l) == darts for l in ll)
                
        my_nGmap = cls(n)
        my_nGmap.darts.update(darts)
        
        for alpha, l in zip(my_nGmap.alpha, ll):
            for a, b in zip(sorted(darts), l):
                alpha[a] = b
                
        my_nGmap.lowest_unused_dart_index = max(darts) + 1
        
        return my_nGmap
    
    @property
    def is_valid(self):
        """
        checks condition 2 and 3 from definition 1
        (condition 1 is always true as a computer probably has finite memory)
        """
 
        for dart in self.darts:
            for alpha in self.alpha:

                """ print(f'dart -> {dart}')
                print(f'alpha[dart] -> {alpha[dart]}')
                print(f'alpha[alpha[dart]] -> {alpha[alpha[dart]]}') """
                if alpha[alpha[dart]] != dart:
                    return False
            for i in range(0, self.n - 1): # n-1 not included
                alpha1 = self.alpha[i]
                for j in range(i + 2, self.n + 1): # n+1 again not included
                    alpha2 = self.alpha[j]
                    if alpha1[alpha2[alpha1[alpha2[dart]]]] != dart:
                        return False
        return True
    
    def reserve_mark(self):
        """
        algorithm 2
        """
        i = max(self.taken_marks) + 1
        self.taken_marks.add(i)
        return i
    
    def free_mark(self, i):
        """
        algorithm 3
        also includes deleting all these marks, making it safe to call everytime
        """
        del self.marks[i]
        self.taken_marks.remove(i)    
    
    def is_marked(self, d, i):
        """
        algorithm 4
        d ... dart
        i ... mark index
        """
        return self.marks[i][d]
    
    def mark(self, d, i):
        """
        algorithm 5
        d ... dart
        i ... mark index
        """
        self.marks[i][d] = True
        
    def unmark(self, d, i):
        """
        algorithm 6
        d ... dart
        i ... mark index
        """
        # same as bla = False
        del self.marks[i][d]
    
    def mark_all(self, i):
        for d in self.darts:
            self.mark(d, i)
    
    def unmark_all(self, i):
        del self.marks[i]
    
    def ai(self, i, d):
        #print(f'ai -> {self.alpha[i][d]}, i -> {i}, d -> {d}')
        self.alpha[i].set_i(i)
        return self.alpha[i][d]
    
    def set_ai(self, i, d, d1):
        assert 0 <= i <= self.n
        #self.custom_alpha[i][d] = d1
        #print(f'd -> {d}\nd1 -> {d1}')
        #self.dart_level[d] = self.level
        self.alpha[i].set_i(i)
        self.alpha[i][d] = d1
        #print(f'alpha in set_ai -> {self.alpha[i][d]}')
        
    def _remove_dart(self, d):

        """
            We are removing the dart from the set.
        """
        self.darts.remove(d)


        print(f'delete -> {d}')

        """
            We are removing the dart from every alpha
        """
        for i in self.all_dimensions:
            del self.alpha[i][d]
    
    def orbit(self, sequence, d):
        """
        algorithm 7
        sequence ... valid list of dimensional indices
        d ... dart
        """
        #print(f'd -> {d}')
        ma = self.reserve_mark()
        self.mark_orbit(sequence, d, ma)
        orbit = self.marks[ma].keys()
        self.free_mark(ma)
        return orbit
    
    def mark_orbit(self, sequence, d, ma):
        """
        used as in algorithm 7 and 8 etc...
        sequence ... valid list of dimension indices
        d ... dart
        ma ... mark to use
        """

        P = [d]
        self.mark(d, ma)
        while P:
            cur = P.pop()
            for i in sequence:
                other = self.alpha[i][cur]
                if not self.is_marked(other, ma):
                    self.mark(other, ma)
                    P.append(other)
    
    def cell_i(self, i, dart):
        """iterator over i-cell of a given dart"""
        return self.orbit(self.all_dimensions_but_i(i), dart)

    def cell_0(self, dart):
        return self.cell_i(0, dart)
    def cell_1(self, dart):
        return self.cell_i(1, dart)
    def cell_2(self, dart):
        return self.cell_i(2, dart)
    def cell_3(self, dart):
        return self.cell_i(3, dart)
    def cell_4(self, dart):
        return self.cell_i(4, dart)
    
    def no_i_cells (self, i=None):
        """
        Counts
            i-cells,             if 0 <= i <= n
            connected components if i is None
        """
        assert i is None or 0 <= i <= self.n
        # return more_itertools.ilen (self.darts_of_i_cells(i))
        return sum ((1 for d in self.darts_of_i_cells(i)))

    @property
    def no_0_cells (self): return self.no_i_cells (0)
    @property
    def no_1_cells (self): return self.no_i_cells (1)
    @property
    def no_2_cells (self): return self.no_i_cells (2)
    @property
    def no_3_cells (self): return self.no_i_cells (3)
    @property
    def no_4_cells (self): return self.no_i_cells (4)
    @property
    def no_ccs     (self): return self.no_i_cells ( )
    
    def darts_of_i_cells(self, i = None):
        """
        algorithm 8
        """
        ma = self.reserve_mark()
        try:
            for d in self.darts:
                if not self.is_marked(d, ma):
                    yield d
                    self.mark_orbit(self.all_dimensions_but_i(i), d, ma)
        finally:
            self.free_mark(ma)
    
    def all_i_cells(self, i = None):
        for d in self.darts_of_i_cells(i):
            yield self.cell_i(i, d)
    
    def all_conected_components(self):
        return self.all_i_cells()
    
    def darts_of_i_cells_incident_to_j_cell(self, d, i, j):
        """
        algorithm 9
        """
        assert i != j
        ma = self.reserve_mark()
        try:
            for e in self.orbit(self.all_dimensions_but_i(j), d):
                if not self.is_marked(e, ma):
                    yield e
                    self.mark_orbit(self.all_dimensions_but_i(j), e, ma)
        finally:
            self.free_mark(ma)
        
    def darts_of_i_cells_adjacent_to_i_cell(self, d, i):
        """
        algorithm 10
        """
        ma = self.reserve_mark()
        try:
            for e in self.orbit(self.all_dimensions_but_i(i), d):
                f = self.alpha[i][e]
                if not self.is_marked(f, ma):
                    yield f
                    self.mark_orbit(self.all_dimensions_but_i(i), f, ma)
        finally:
            self.free_mark(ma)
        
    def all_dimensions_but_i (self, i=None):
        """Return a sorted sequence [0,...,n], without i, if 0 <= i <= n"""
        assert i is None or 0 <= i <= self.n
        return [j for j in range (self.n+1) if j != i]
    
    @property
    def all_dimensions(self):
        return self.all_dimensions_but_i()
    
    def is_i_free(self, i, d):
        """
        definiton 2 / algorithm 11
        """
        return self.alpha[i][d] == d
        
    def is_i_sewn_with(self, i, d):
        """
        definiton 2
        """
        d2 = self.alpha[i][d]
        return d != d2, d2
    
    def create_dart(self):
        """
        algorithm 12
        """
        d = self.lowest_unused_dart_index
        self.lowest_unused_dart_index += 1
        self.darts.add(d)
        for alpha in self.alpha:
            alpha[d] = d
        return d
    
    def remove_isolated_dart(self, d):
        """
        algorithm 13
        """
        assert self.is_isolated(d)
        self.remove_isolated_dart_no_assert(d)
        
    def remove_isolated_dart_no_assert(self, d):
        self.darts.remove(d)
        for alpha in self.alpha:
            del alpha[d]
    
    def is_isolated(self, d):
        for i in range(self.n + 1):
            if not self.is_i_free(i, d):
                return False
        return True
    
    def increase_dim(self):
        """
        algorithm 15 in place
        """
        self.n += 1
        self.alpha.append(dict((d,d) for d in self.darts))
        
    def decrease_dim(self):
        """
        algorithm 16 in place
        """
        assert all(self.is_i_free(self.n, d) for d in self.darts)
        self.decrease_dim_no_assert()
    
    def decrease_dim_no_assert(self):
        del self.alpha[self.n]
        self.n -= 1
    
    def index_shift(self, by):
        self.darts = {d + by for d in self.darts}
        self.alpha = [{k + by : v + by for k, v in a.items()} for a in self.alpha]
        for mark in self.marks:
            new_dict = {key + by : value for key, value in self.marks[mark].items()}
            self.marks[mark].clear()
            self.marks[mark].update(new_dict) #this is done to preserve default dicts
        self.lowest_unused_dart_index += by
        
    def merge(self, other):
        """
        algorithm 17 in place
        """
        assert self.n == other.n
        self.taken_marks.update(other.taken_marks)
        shift = max(self.darts) - min(other.darts) + 1
        other.index_shift(shift)
        
        self.darts.update(other.darts)
        for sa, oa in zip(self.alpha, other.alpha):
            sa.update(oa)
        for mk in other.marks:
            self.marks[mk].update(other.marks[mk])
        self.taken_marks.update(other.taken_marks)
        self.lowest_unused_dart_index = other.lowest_unused_dart_index
        
    def restrict(self, D):
        """
        algorithm 18
        """
        raise NotImplementedError #boring
    
    def sew_seq(self, i):
        """
        indices used in the sewing operations
        (0, ..., i - 2, i + 2, ..., n)
        """
        return chain(range(0, i - 1), range(i + 2, self.n + 1))
    
    def sewable(self, d1, d2, i):
        """
        algorithm 19
        tests wether darts d1, d2 are sewable along i
        returns bool
        """
        if d1 == d2 or not self.is_i_free(i, d1) or not self.is_i_free(i, d2):
            return False
        try:
            f = dict()
            for d11, d22 in strict_zip(self.orbit(self.sew_seq(i), d1), self.orbit(self.sew_seq(i), d2), strict = True):
                f[d11] = d22
                for j in self.sew_seq(i):
                    if self.alpha[j][d11] in f and f[self.alpha[j][d11]] != self.alpha[j][d22]:
                        return False
        except ValueError: #iterators not same length
            return False
        return True
    
    def sew(self, d1, d2, i):
        """
        algorithm 20
        """
        assert self.sewable(d1, d2, i)
        self.sew_no_assert(d1, d2, i)
        
    def sew_no_assert(self, d1, d2, i):
        for e1, e2 in strict_zip(self.orbit(self.sew_seq(i), d1), self.orbit(self.sew_seq(i), d2), strict = True):
            self.alpha[i][e1] = e2
            self.alpha[i][e2] = e1
    
    def unsew(self, d, i):
        """
        algorithm 21
        """
        assert not self.is_i_free(i, d)
        for e in self.orbit(self.sew_seq(i), d):
            f = self.alpha[i][e]
            self.alpha[i][f] = f
            self.alpha[i][e] = e
    
    def incident (self, i, d1, j, d2):
        """
        checks wether the i-cell of d1 is incident to the j-cell of d2
        """
        for e1, e2 in product(self.cell_i(i, d1), self.cell_i(j, d2)):
            if e1 == e2:
                return True
        return False
    
    def adjacent(self, i, d1, d2):
        """
        checks wether the i-cell of d1 is adjacent to the i-cell of d2
        """
        first_cell = self.cell_i(i, d1)
        second_cell = set(self.cell_i(i, d2))
        for d in first_cell:
            if self.alpha[i][d] in second_cell:
                return True
        return False
    
    # Contractablilty & Removability

    """
        The next three methods are useful for checking the contractability and removability of darts.
    """
    
    def _is_i_removable_or_contractible(self, i, dart, rc):
        """
        Test if an i-cell of dart is removable/contractible:

        i    ... i-cell
        dart ... dart
        rc   ... +1 => removable test, -1 => contractible test
        """
        assert dart in self.darts
        assert 0 <= i <= self.n
        assert rc in {-1, +1}

        if rc == +1:  # removable test
            if i == self.n  : return False
            if i == self.n-1: return True
        if rc == -1:  # contractible test
            if i == 0: return False
            if i == 1: return True

        for d in self.cell_i(i, dart):
            if self.alpha[i+rc][self.alpha[i+rc+rc][d]] != self.alpha[i+rc+rc][self.alpha[i+rc][d]]:
                return False
        return True

    def is_i_removable(self, i, dart):
        """True if i-cell of dart can be removed"""
        return self._is_i_removable_or_contractible(i, dart, rc=+1)

    def is_i_contractible(self, i, dart):
        """True if i-cell of dart can be contracted"""
        return self._is_i_removable_or_contractible(i, dart, rc=-1)

    """
        The i_remove_contract method is used for removing a certain dart from the n-Gmap.
    """
    
    def _i_remove_contract(self, i, dart, rc, skip_check=False):
        """
        Remove / contract an i-cell of dart
        d  ... dart
        i  ... i-cell
        rc ... +1 => remove, -1 => contract
        skip_check ... set to True if you are sure you can remove / contract the i-cell
        """
        logging.debug (f'{"Remove" if rc == 1 else "Contract"} {i}-Cell of dart {dart}')

        if not skip_check:
            assert self._is_i_removable_or_contractible(i, dart, rc),\
                f'{i}-cell of dart {dart} is not {"removable" if rc == 1 else "contractible"}!'

        """
            Every time the checking is over I assume that I can increment the variable that keeps trace of
            the levels because the dart is removed/contracted, for sure.
        """
        self.level += 1
        #print(f'level -> {self.level}')

        
        #print(type(self.alpha[i]))

        i_cell = set(self.cell_i(i, dart))  # mark all the darts in ci(d)

        #print(f'i-cell -> {i_cell}')
        #print(f'\n{i}-cell to be removed {i_cell}')
        for d in i_cell:
            d1 = self.ai (i,d) # d1 ← d.Alphas[i];
            if d1 not in i_cell:  # if not isMarkedNself(d1,ma) then
                # d2 ← d.Alphas[i + 1].Alphas[i];
                #print(f'd1 -> {d1}')
                d2 = self.ai (i+rc,d)
                d2 = self.ai (i   ,d2)
                while d2 in i_cell: # while isMarkedNself(d2,ma) do
                    # d2 ← d.Alphas[i + 1].Alphas[i];
                    d2 = self.ai (i+rc,d2)
                    d2 = self.ai (i   ,d2)
                logging.debug (f'Modifying alpha_{i} of dart {d1} from {self.ai (i,d1)} to {d2}')

                self.set_ai(i,d1,d2) # d1.Alphas[i] ← d2;

        
        """
            In that for loop, in addition to remove the dart given in input,
            I also check if involutions of this dart are different from the
            implicitly ones. If they are different, then they will move into
            the passive part, otherwise nothing will be stored.

            I wanto to say that implementation is been provided to work with
            2-Gmaps. For that reason there are only three if statements to check
            which j-value I am analysing.
        """
        for d in i_cell:  # foreach dart d' ∈ ci(d) do
            for j in self.all_dimensions:
                if j == 0:
                    if self.alpha[j][d] != self.alpha[j].get_alpha0(d):
                        self.custom_alpha[j][d] = self.alpha[j][d]

                if j == 1:
                    if self.alpha[j][d] != self.alpha[j].get_alpha1(d):
                        self.custom_alpha[j][d] = self.alpha[j][d]

                if j == 2:
                    if self.alpha[j][d] != self.alpha[j].get_alpha2(d):
                        self.custom_alpha[j][d] = self.alpha[j][d]
                
            self.dart_level[d] = self.level

            #print(f'dart that will be removed -> {d}')
            self._remove_dart (d)  # remove d' from gm.Darts;

    """
        Method I need to call to remove a certain dart from the n-Gmap.
    """
    def _remove(self, i, dart, skip_check=False):
        """Remove i-cell of dart"""
        self._i_remove_contract(i, dart, rc=+1, skip_check=skip_check)

    """
        Method I need to call to contract a certain dart from the n-Gmap.
    """
    def _contract(self, i, dart, skip_check=False):
        """Contract i-cell of dart"""
        self._i_remove_contract(i, dart, rc=-1, skip_check=skip_check)

    """
        Useful method to have the summary of the current n-Gmap.
    """
    def __repr__(self):
        out = f"{self.n}dGmap of {len(self.darts)} darts:\n"
        for i in range(self.n + 1): # n+1 is not included
            out += f" {i}-cells: {self.no_i_cells(i)}\n"
        out += f" ccs: {self.no_ccs}"
        return out


    """
        Method to check the initial involutions of the n-Gmap.
    """
    def print_starting_alpha(self):

        print(f'\nD[i]    | ', end= " ")
        for i in self.darts:
            print(f'{i} |', end= " ")

        for i in range(0, self.n+1):
            print(f'\nAlpha_{i} | ', end= " ")
            for k in self.darts:
                if i == 0:
                    print(f'{self.impl_dict.get_alpha0(k)} |', end= " ")
                elif i == 1:
                    print(f'{self.impl_dict.get_alpha1(k)} |', end= " ")
                else:
                    print(f'{self.impl_dict.get_alpha2(k)} |', end= " ")


    """
        Method to print the active part (current Gmap) that is stored into the data structure.
    """
    def print_alpha(self):
        for i in range(0, self.n + 1):
            print(f'\nAlpha_{i} -> {self.alpha[i]}')

    
    def print_final_alpha(self):
        
        print(f'\nD[i]    | ', end= " ")
        for i in self.darts:
            print(f'{i} |', end= " ")

        for i in range(0, self.n+1):
            print(f'\nAlpha_{i} | ', end= " ")
            for k in self.darts:
                if i == 0:
                    print(f'{self.alpha[i][k]} |', end= " ")
                elif i == 1:
                    print(f'{self.alpha[i][k]} |', end= " ")
                else:
                    print(f'{self.alpha[i][k]} |', end= " ")
        
    """
        Method to print the passive part that is stored into the data structure.
    """
    def print_custom(self):
        """ print(f'\n\nDart    | ', end= " ")
        for i in self.custom_alpha[0].keys():
            print(f'{i} |', end= " ")

        for i in range(0, self.n+1):
            print(f'\nAlpha_{i} | ', end= " ")
            for j in self.custom_alpha[i].values():
                    print(f'{j} |', end= " ") """

        print(self.custom_alpha[0])
        print(self.custom_alpha[1])
        print(self.custom_alpha[2])

    """
        Method to check the history of the pyramid.
    """
    def print_history_levels(self):
        print(f'\n\nHistory')

        print(f'Dart  | Level')

        for k, v in zip(self.dart_level.keys(), self.dart_level.values()):
            print(f'  {k}   |   {v}')



    def _insert_until_level(self, level, filename=None, i=None,):   

        l = []
        for k in reversed(self.dart_level):
            
            if self.dart_level[k] > level:
                """
                    If you over this condition It means you can reconstruct something.
                """
                l.append(k)
                self.darts.add(k)
                print(f'dart {k} added to the set of darts')

                for j in range(0, self.n + 1):
                        # k = 75
                        try:
                            self.alpha[j][self.custom_alpha[j][k]] = k
                        except KeyError:
                            self.alpha[j].set_i(j)
                            self.alpha[j][self.alpha[j][k]] = k ############################## alpha0[alpha0[75] -> 74] = 75

                        try:
                            
                            self.alpha[j][k] = self.custom_alpha[j][k]
                        except KeyError:
                            if j == 0:
                                if self.alpha[j][k] != self.alpha[j].get_alpha0(k):
                                    #self.alpha[j][k] = self.alpha[j][k] ################## alpha0[75] = implicitly_encoding, actually
                                    self.alpha[j][k] = self.alpha[j].get_alpha0(k)

                            if j == 1:
                                if self.alpha[j][k] != self.alpha[j].get_alpha1(k):
                                    self.alpha[j][k] = self.alpha[j].get_alpha1(k)

                            if j == 2:
                                if self.alpha[j][k] != self.alpha[j].get_alpha2(k):
                                    self.alpha[j][k] = self.alpha[j].get_alpha2(k)

                        try:
                            del self.custom_alpha[j][k]
                        except KeyError:
                            del self.alpha[j][self.alpha[j][k]]
                
        for el in l:
            del self.dart_level[el]

    def plot(self):
        plot(self.darts)