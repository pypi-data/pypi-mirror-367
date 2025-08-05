import re
import sys
import textwrap
from collections.abc import Sequence
from itertools import chain

from genbank.codons import Last
from genbank.codons import Next
from genbank.codons import Codons
from genbank.feature import Feature
from genbank.feature import grouper
from genbank.sequence import Seq
from genbank.translate import Translate

def wrap(text, width=10):
	for i in range(0, len(text), width):
		yield text[i:i+width]

def rev_comp(dna):
	a = 'acgtrykmbvdh'
	b = 'tgcayrmkvbhd'
	tab = str.maketrans(a,b)
	return dna.translate(tab)[::-1]

def nint(s):
	return int(s.replace('<','').replace('>',''))

def rmap(func, items):
	out = list()
	for item in items:
		if isinstance(item, Sequence) and not isinstance(item, str):
			out.append(type(item)(rmap(func,item)))
		else:
			out.append(func(item))
	return type(items)(out)

def recursive_map(func, items):
    return (recursive_map(func, x) if isinstance(x, tuple) else func(x) for x in items)


class Locus(dict):
	def __init__(self, name='', dna=''):
		if not hasattr(self, 'feature'):
			self.feature = Feature
		#self.name = name
		self.dna = dna.lower()
		#self.codons = dict()
		self.translate = Translate()
		self.strand = 1
		self.groups = dict()
		#self.groups['LOCUS'] = [name.replace(' ','')] if name else []
		#self.groups['LOCUS'] = [name] if name else []
		#self.groups['FEATURES'] = ['']
		#self.groups['ORIGIN'] = ['']

	def name(self, name=None):
		if not name:
			if 'LOCUS' in self.groups:
				return self.groups['LOCUS'][0].split(' ')[0]
			return ''
		self.groups['LOCUS'] = [name]
		
	def __eq__(self, other):
		return (self == other)

	def __hash__(self):
		return id(self)

	def __init_subclass__(cls, feature=Feature, **kwargs):
		'''this method allows for a Feature class to be modified through inheritance in other code '''
		super().__init_subclass__(**kwargs)
		cls.feature = feature

	def molecule(self):
		if len(locus) > 2:
			return locus[3]
		else:
			return 'DNA'

	def seq(self, left=0, right=None, strand=None):
		# this should always refer to zero based indexing
		#if strand is None:
		#	strand = self.strand
		if left < 0:
			left = None
		if right and right < 0:
			right = 0
		if strand and strand < 0:
			return Seq(rev_comp(self.dna[left : right]))
		else:
			return Seq(         self.dna[left : right] )

	def length(self):
		return len(self.dna)

	def gc_content(self, seq=None):
		if seq is not None:
			#a = seq.count('a') + seq.count('A')
			c = seq.count('c') + seq.count('C')
			g = seq.count('g') + seq.count('G')
			#t = seq.count('t') + seq.count('T')
			return (c+g) / len(seq) #(a+c+g+t)
		elif not hasattr(self, "gc"):
			#a = self.dna.count('a') + self.dna.count('A')
			c = self.dna.count('c') + self.dna.count('C')
			g = self.dna.count('g') + self.dna.count('G')
			#t = self.dna.count('t') + self.dna.count('T')
			self.gc = (c+g) / len(self.dna) # (a+c+g+t)
		return self.gc

	def pcodon(self, codon):
		codon = codon.lower()
		seq = self.dna + rev_comp(self.dna)
		p = dict()
		p['a'] = seq.count('a') / len(seq)
		p['c'] = seq.count('c') / len(seq)
		p['g'] = seq.count('g') / len(seq)
		p['t'] = seq.count('t') / len(seq)
		return p[codon[0]] * p[codon[1]] * p[codon[2]]

	def rbs(self):
		for feature in self:
			if feature.type == 'CDS':
				if feature.strand > 0:
					start = feature.left()+3
					feature.tags['rbs'] = self.seq(start-30,start)
				else:
					start = feature.right()
					feature.tags['rbs'] = rev_comp(self.seq(start,start+30))
	
	def features(self, include=None, exclude=None):
		for feature in self:
			if not include or feature.type in include:
				yield feature

	def add_feature(self, key, strand, pairs, tags=dict()):
		"""Add a feature to the factory."""
		#feature = self.feature
		strand = 44 - ord(strand) if strand in ['+','-'] else 0 if strand in ['.'] else int(strand)
		feature = self.feature(key, strand, pairs, self, tags=tags)
		if feature not in self:
			self[feature] = len(self)
		return feature

	def read_feature(self, line):
		"""Add a feature to the factory."""
		key = line.split()[0]
		val = line.split()[1]
		#partial  = 'left' if '<' in line else ('right' if '>' in line else False)
		strand = -1 if 'complement' in line else 1
		# this is for weird malformed features
		if ',1)' in line:
			line = line.replace( ",1)" , ",1..1)" )
		#pairs = [pair.split('..') for pair in re.findall(r"<*\d+\.\.>*\d+", line)]
		#pairs = [map(int, pair.split('..')) for pair in re.findall(r"<?\d+\.{0,2}>?\d+", line.replace('<','').replace('>','') )]
		#pairs = [ pair.split('..') for pair in re.findall(r"<?\d+\.{0,2}>?[-0-9]*", line) ]
		pairs = [ pair.split('..') for pair in re.findall(r"<?\d+\.{0,2}>?\d*", val) ]
		# tuplize the pairs
		pairs = tuple([tuple(pair) for pair in pairs])
		feature = self.add_feature(key, strand, pairs)
		return feature

	def gene_coverage(self):
		''' This calculates the protein coding gene coverage, which should be around 1 '''
		cbases = tbases = 0	
		index = [ [False] * len(self.dna) , [False] * len(self.dna)]
		for feature in self.features(include=['CDS','tRNA']):
			for locations in grouper(feature.loc(), 3):
				for location in locations:
					if location:
						index[(feature.strand >> 1) * -1][location-1] = True
					break
		cbases += sum([item for sublist in index for item in sublist])
		tbases += len(self.dna) / 3
		return cbases , tbases
	
	def gc_fp(self):
		fp = [0,0,0]
		for feature in self.features(include=['CDS']):
			for codon in feature.codons():
				for i,base in enumerate(codon):
					fp[i] += (ord(base) >> 1 ) & 3 % 2
		return fp

	def testcode(self):
		# THIS IS A REIMPLEMENTATION OF THE ORIGINAL TESTCODE METHOD 
		# BY FICKET 1982
		pos = [
				{ 'a': .22, 'c': .23, 'g': .08, 't': .09},
				{ 'a': .20, 'c': .30, 'g': .08, 't': .09},
				{ 'a': .34, 'c': .33, 'g': .16, 't': .20},
				{ 'a': .45, 'c': .51, 'g': .27, 't': .54},
				{ 'a': .68, 'c': .48, 'g': .48, 't': .44},
				{ 'a': .58, 'c': .66, 'g': .53, 't': .69},
				{ 'a': .93, 'c': .81, 'g': .64, 't': .68},
				{ 'a': .84, 'c': .70, 'g': .74, 't': .91},
				{ 'a': .68, 'c': .70, 'g': .88, 't': .97},
				{ 'a': .94, 'c': .80, 'g': .90, 't': .97}
				]
		con = [
				{ 'a': .21, 'c': .31, 'g': .29, 't': .58},
				{ 'a': .81, 'c': .39, 'g': .33, 't': .51},
				{ 'a': .65, 'c': .44, 'g': .41, 't': .69},
				{ 'a': .67, 'c': .43, 'g': .41, 't': .56},
				{ 'a': .49, 'c': .59, 'g': .73, 't': .75},
				{ 'a': .62, 'c': .59, 'g': .64, 't': .55},
				{ 'a': .55, 'c': .64, 'g': .64, 't': .40},
				{ 'a': .44, 'c': .51, 'g': .47, 't': .39},
				{ 'a': .49, 'c': .64, 'g': .54, 't': .24},
				{ 'a': .28, 'c': .82, 'g': .40, 't': .28}
				]
		wp = {'a':.26,'c':.18,'g':.31,'t':.33}
		wc = {'a':.11,'c':.12,'g':.15,'t':.14}
		content = {
		'a':[0,0,0],
		'c':[0,0,0],
		'g':[0,0,0],
		't':[0,0,0]
		}
		for i,base in enumerate(self.seq()):
			content[base][i%3] += 1
		position = dict()
		for base in 'acgt':
			position[base] = max(content[base]) / (min(content[base])+1)
		p = 0
		for base in 'acgt':
			n = int(str(position[base])[2]) if position[base] < 2 else 9
			p += pos[n][base] * wp[base]
		for base in 'acgt':
			percent = sum(content[base]) / self.length()
			n = int(str((percent-0.17) * 5 )[2])+1 if percent > 0.17 else 0
			p += con[n][base] * wc[base]
		if p <= 0.75:
			return 'noncoding'
		elif p < 0.95:
			return 'no opinion'
		else:
			return 'coding'

	def write(self, args):
		if isinstance(args, str):
			if hasattr(self, args):
				getattr(self, args)(sys.stdout)
			else:
				raise ValueError('invalid outfile format')
		else:
			getattr(self, args.format)(args.outfile)

	def fasta(self, outfile):
		outfile.write(">")
		outfile.write(self.name())
		outfile.write("\n")
		outfile.write(self.seq())
		outfile.write("\n")

	def genbank(self, outfile=sys.stdout):
		for group,values in chain(self.groups.items(), [[None,[True, False]]] ):
			for value in values:
				if group == 'LOCUS':
					outfile.write('LOCUS       ')
					cols = self.groups['LOCUS'][0].split(' ')
					# I eventually need to properly format the locus line
					outfile.write(self.name().ljust(9))
					outfile.write(str(len(self.dna)).rjust(19))
					outfile.write(' bp ')
					if 'bp' in cols:
						outfile.write(' '.join(cols[cols.index('bp')+1:]))
					else:
						outfile.write('\n')
					continue
				elif group == 'FEATURES' or (not group and value and 'FEATURES' not in self.groups):
					outfile.write('FEATURES             Location/Qualifiers\n')
					for feature in self:
						feature.write(outfile)
				elif group == 'ORIGIN' or (not group and not value and 'ORIGIN' not in self.groups):
					# should there be spaces after ORIGIN?
					outfile.write('ORIGIN      ')
					i = 0
					for block in wrap(self.dna, 10):
						if(i%60 == 0):
							outfile.write('\n')
							outfile.write(str(i+1).rjust(9))
							outfile.write(' ')
							outfile.write(block.lower())
						else:
							outfile.write(' ')
							outfile.write(block.lower())
						i += 10
				elif group == 'BASE':
					for value in values:
						outfile.write(group)
						outfile.write(' ')
						outfile.write(value)
				elif group:
					outfile.write(group.ljust(12))
					outfile.write(value)
		outfile.write('\n')
		outfile.write('//')
		outfile.write('\n')

	def gff3(self, outfile=sys.stdout):
		outfile.write('>Feature')
		outfile.write(' ') # should this be a space or a tab?
		outfile.write(self.name())
		outfile.write('\n')
		outfile.write('1')
		outfile.write('\t')
		outfile.write(str(self.length()))
		outfile.write('\t')
		outfile.write('REFERENCE')
		outfile.write('\n')
		for feature in self.features(include=['CDS']):
			pairs = [list(item)[::feature.strand] for item in feature.pairs][::feature.strand]
			pair = pairs.pop(0)
			outfile.write(pair[0])
			outfile.write("\t")
			outfile.write(pair[-1])
			outfile.write("\t")
			outfile.write(feature.type)
			for pair in pairs:
				outfile.write("\n")
				outfile.write(pair[0])
				outfile.write("\t")
				outfile.write(pair[-1])
			for tag,values in feature.tags.items():
				for value in values:
					outfile.write("\n")
					outfile.write("\t\t\t")
					outfile.write(str(tag))
					outfile.write("\t")
					if value is None:
						pass
					elif isinstance(value,str) and value[0] == '"' and value[-1] == '"':
						outfile.write(value[1:-1])
					else:
						outfile.write(str(value))
			outfile.write("\n")

	def gff(self, outfile=sys.stdout):
		outfile.write("##gff-version 3\n")
		for feature in self:
			outfile.write(self.name())
			outfile.write("\t")
			if 'SOURCE' in self.groups:
				outfile.write(self.groups['SOURCE'][0].split('\n')[0])
			else:
				outfile.write('None')
			outfile.write("\t")
			outfile.write(feature.type)
			outfile.write("\t")
			outfile.write(feature.pairs[0][0])
			outfile.write("\t")
			outfile.write(feature.pairs[-1][-1])
			outfile.write("\t")
			if hasattr(feature, 'score'):
				outfile.write(str(feature.score))
			else:
				outfile.write('.')
			outfile.write("\t")
			outfile.write(str(feature.strand).replace('-1','-').replace('1','+').replace('0','+') )
			outfile.write("\t")
			outfile.write(".")
			outfile.write("\t")
			# write ID for the feature
			outfile.write("ID=")
			outfile.write(self.name() + "_CDS_[" + feature.locations() + "]")
			for tag,values in feature.tags.items():
				outfile.write(";")
				for value in values:
					outfile.write(str(tag))
					if value is None:
						pass
					elif isinstance(value,str) and value[0] == '"' and value[-1] == '"':
						outfile.write("=")
						outfile.write(value[1:-1])
					else:
						outfile.write("=")
						outfile.write(str(value))
					outfile.write(";")
			outfile.write("\n")

	def fna(self, outfile=sys.stdout):
		for feature in self.features(include=['CDS']):
			outfile.write( feature.fna() )

	def faa(self, outfile=sys.stdout):
		for feature in self.features(include=['CDS']):
			outfile.write( feature.faa() )

	def tabular(self, outfile=sys.stdout):
		for feature in self: #.features(include=['CDS']):
			outfile.write(str(feature))
			outfile.write("\t")
			outfile.write(feature.seq())
			outfile.write("\n")

	def last(self, n, codons, strand):
		# this needs to be 0-based indexing
		if isinstance(codons, str):
			codons = [codons.lower()]
		codons = [codon.lower() for codon in codons]
		if strand > 0:
			irange = range(n,            -1, -3)
		else:
			irange = range(n, self.length(), +3)
		for i in irange:
			if self.seq(i,i+3,strand) in codons:
				return i
		return None

	def next(self, n, codons, strand):
		if isinstance(codons, str):
			codons = [codons]
		codons = [codon.lower() for codon in codons]
		if strand > 0:
			irange = range(n, self.length(), +3)
		else:
			irange = range(n,            -1, -3)
		for i in irange:
			if self.seq(i,i+3,strand) in codons:
				return i
		return None

	def nearest(self, n, codons, strand):
		_last = self.last(n,strand,codons)
		if not _last:
			_last = 0
		_next = self.next(n,strand,codons)
		if not _next:
			_next = self.length()
		if n - _last < _next - n:
			return _last
		else:
			return _next

	def distance(self, n, strand, codons):
		nearest = self.nearest(n, strand, codons)
		return n - nearest if nearest < n else nearest - n

	def codon_rarity(self, codon=None):
		if not hasattr(self, 'rarity'):
			seen = {-1:dict(), +1:dict()}
			self.rarity = {a+b+c : 0 for a in 'acgt' for b in 'acgt' for c in 'acgt'}
			for feature in self:
				if feature.type == 'CDS':
					#for _codon, _loc in zip(feature.codons(), feature.codon_locations()):
					#	if _codon in self.rarity and _loc not in seen[feature.strand]:
					for _codon in feature.codons():
						if _codon in self.rarity:
							self.rarity[_codon] += 1
					#		seen[feature.strand][_loc] = True
		total = sum(self.rarity.values())
		self.rarity = {codon:self.rarity[codon]/total for codon in self.rarity}
		if codon in self.rarity:
			return self.rarity[codon]
		elif codon:
			return None
		else:
			return self.rarity

	def slice(self, left, right):
		if left > right:
			left,right = right+1,left+1
			self.strand = -1
		self.dna = self.seq(left,right)
		to_delete = list()
		for feature in self.keys():
			if feature.right() - 1 < left or feature.left() > right:
				to_delete.append(feature)
			else:
				# whew there is a lot going on here
				f0 = lambda x : int(x.replace('<','').replace('>',''))
				f1 = lambda x : '<1' if f0(x) - left < 1 else ('>'+str(self.length()) if f0(x) - left > self.length() else f0(x) - left)
				f2 = lambda x : str(f1(x))
				feature.pairs = rmap(f2, feature.pairs)
		for feature in to_delete:
			del self[feature]
		return self



