from compassheadinglib import Compass
from compassheadinglib.common import Heading

from random import uniform
from json import load
from pathlib import Path
from itertools import chain
from collections import Counter
from pprint import pprint

_compass=Compass.asList()

#wrap around test
assert Compass[0].name == Compass[-1].name
assert Compass[0].abbr == Compass[-1].abbr
assert Compass[0].order == Compass[-1].order
assert Compass[0].azimuth < Compass[-1].azimuth

#monotonic range increase tests
last=-1
items_monotocicity=[]
for i in Compass:
	items_monotocicity.append(last < i.azimuth)
	last=i.azimuth
assert all(items_monotocicity)

#check that data contains only order 1-4
number_of_heading_levels=4
assert set(range(1,number_of_heading_levels+1)) == set([i.order for i in Compass])

#count how entrys there are for each order
#remember that order 1 has 5 values because 'North' get repeated as the first and last elements of the Compass object
assert len([i for i in Compass if i.order==1]) == 5
assert len([i for i in Compass if i.order==2]) == 4
assert len([i for i in Compass if i.order==3]) == 8
assert len([i for i in Compass if i.order==4]) == 16


#manual range selection tests
manual_range_test_azimuth=57
manul_range_test_names=['East','Northeast','East-Northeast','Northeast by East']
for i in zip(range(0,number_of_heading_levels),manul_range_test_names):
	assert str(Compass.findHeading(1,i[0]+1)) == 'North'
	assert str(Compass.findHeading(manual_range_test_azimuth,i[0]+1)) == i[1]

#randomized range selection test
#for each direction in a level (remember that a level also countains any items on any lower 
#numbered level) do FUZZ_IN_TEST_COUNT tests iside it's range (i.e. the range is say 10-20 
#and the test value is 14) return the correct item and do FUZZ_OUT_TEST_COUNT tests outside
# it's range (i.e. the range is say 1 0-20 and the test value is 42). Test values are randomly
#selected each run. This test implicity also tests the Heading and _Headings object.

number_of_random_range_selections=10000

slice_angle=11.25
parent_angles=[0,90,180,270]

angle_list=[uniform(0.0, 360.0) for i in range(0,number_of_random_range_selections)]

for angle in angle_list:
	res=int(angle//slice_angle)
	#this test can be off by one since it's simpler then the real logic, but as long as one or one-off by +1 matches across 
	#a large random set we're good

	assert Heading(**_compass[res])==Compass.findHeading(angle,4) or Heading(**_compass[res+1])==Compass.findHeading(angle,4)

#manual spot tests of relativity tests (greater than, less than, etc.)
#also tests that calling a Headings object directly is functionally the same as calling the findHeading method
assert Compass(0,1)==Compass.findHeading(12,1)
assert Compass(0,1)==Compass.findHeading(12,2)
assert Compass(0,1)<Compass.findHeading(12,3)
assert Compass(0,1)<Compass.findHeading(12,4)
assert Compass(12,3)>Compass.findHeading(0,1)
assert Compass(12,4)>Compass.findHeading(0,1)

#randomized test of relativity tests (greater than, less than, etc.)

number_of_random_relativity_tests=10000

for relative_a,relative_b in [(uniform(0,360),uniform(0,360)) for i in range(0,number_of_random_relativity_tests)]:
	#print(relative_a,relative_b,relative_a//slice_angle,relative_b//slice_angle,abs(relative_a-relative_b),Compass.findHeading(relative_a),Compass.findHeading(relative_b))

	if (relative_a//slice_angle) == (relative_b//slice_angle):
		assert Compass.findHeading(relative_a,order=3) == Compass.findHeading(relative_b,order=3)
	
	elif  ((relative_a//slice_angle) < (relative_b//slice_angle)) and abs(relative_a-relative_b)<slice_angle:
		assert Compass.findHeading(relative_a,order=4) <= Compass.findHeading(relative_b,order=4)
	elif  ((relative_a//slice_angle) > (relative_b//slice_angle)) and abs(relative_a-relative_b)<slice_angle:
		assert Compass.findHeading(relative_a,order=4) >= Compass.findHeading(relative_b,order=4)

	elif  (relative_a//slice_angle) < (relative_b//slice_angle):
		assert Compass.findHeading(relative_a,order=4) < Compass.findHeading(relative_b,order=4)
	elif  (relative_a//slice_angle) > (relative_b//slice_angle):
		assert Compass.findHeading(relative_a,order=4) > Compass.findHeading(relative_b,order=4)

	else:
		print('Impossible relationship: {},{}'.format(relative_a,relative_b))
		assert False
print('All functionality tests have passed')

def flatten(x):
	return list(chain.from_iterable(x))

data_file_path=Path(__file__).parent/'../compassheadinglib/compass_data.json'
_json_data=load(open(data_file_path,'rt'))

#get all unique language codes in the dataset
all_langs=list(sorted(set(flatten([i['Lang'].keys() for i in _json_data]))))

for heading in _json_data:
	for lang in all_langs:
		#all languages must be present in all headings
		assert lang in heading['Lang'], f'{lang} missing from {heading['Azimuth']}'
		
		#check that structure is well formed
		assert 'Heading' in heading['Lang'][lang]
		assert 'Abbreviation' in heading['Lang'][lang]

llm_heading_instructrions="""
You are a translator working on a project to provide a multi-lingual compass. We have been translating the names of compass headings to several languages automatically but that system has had some issues. You are manually fixing the bad or duplicate translations. You will provide for each task an answer consisting of a seven column csv. The first field is degrees, the second is the differentiated translation, the third field is the abbreviation of the differentiated translation (which also must be different and reflect the new phrase) and the forth is a boolean of if this is the original term or not. The fifth field is the original term to be differentiated. The sixth term is the ISO language code appropriate for this term. The final field will always be 'Heading'. The expected header of the output is:
degrees,differentiated_translation,abbreviation,is_original,original_term,language_code,apply_to
"""

llm_abbr_instructions="""
You are a translator working on a project to provide a multi-lingual compass. We have been translating the names of compass headings to several languages automatically but that system has had some issues. You are manually fixing the bad or duplicate translated abbreviations. You are only changing the abbreviations and not the heading names themselves. You will provide for each task an answer consisting of a seven column csv. The first field is degrees, the second is the original name of the heading you are abbreviating. The third will be the differentiated_abbreviation and the forth is a boolean of if the differentiated_abbreviation is the same as the original abbreviation is the original abbreviation or not. The fifth field is the original abbreviation to be differentiated. The sixth term is the ISO language code appropriate for this term. The final field will always be 'Abbr'. The expected header of the output is:
degrees,original_heading_name,differentiated_translation,abbreviation,is_original,original_term,language_code, apply_to
"""

for lang in all_langs:
	langCompass=[i['Lang'][lang] | i for i in _json_data]

	print(lang,len(langCompass),len(set([i['Heading'] for i in langCompass])),len(set([i['Abbreviation'] for i in langCompass])),end='\t')
	#no duplicate heading names
	try:
		assert (len(langCompass)-1)==len(set([i['Heading'] for i in langCompass])),f'Not all Headings are unique for {lang}'
	except AssertionError as e:
		print('Fail')
		c=Counter([i['Heading'] for i in langCompass])
		a=Counter([i['Abbreviation'] for i in langCompass])

		prompt=''
		names_and_abbr='Already used names that must not be repreated are: '+(', '.join([i[0] for i in c.most_common() if i[1]==1 ]))[:-2]
		names_and_abbr=names_and_abbr+' \nAlready used abbreviations that must not be repreated are: '+(', '.join([i[0] for i in a.most_common() if i[1]==1 ]))[:-2]
		llm_paste=llm_heading_instructrions+' '+names_and_abbr+'.\n'
		for n in c.most_common():
			if n[1]>1:
				prompt=prompt+f'\nPlease differentiate the translation {lang} term "{n[0]}".  An automatic translation tool provided this name for {n[1]} headings:"'

				az=[i['Azimuth'] for i in langCompass if n[0]==i['Heading']]
				if not (len(az)==2 and 0 in az and 360 in az): #this is North, it's expected to be duplicated
					print(n[0],az)
					for h in az:
						h_en=Compass(h)
						prompt=prompt+f'{h}° (in English "{h_en}"), '
		
					llm_paste=llm_paste+prompt[:-2]+'. '
		
		print(llm_paste)

		raise e
	
	
	#no duplicate heading abbreviations
	try:
		assert (len(langCompass)-1)==len(set([i['Abbreviation'] for i in langCompass])),f'Not all Abbreviations are unique for {lang}'
	except AssertionError as e:
		
		print('Fail')
		
		c=Counter([i['Abbreviation'] for i in langCompass])
		prompt=''
		
		names_and_abbr='Already used abbreviations that must not be repreated are: '+(', '.join([i[0] for i in c.most_common() if i[1]==1 ]))[:-2]

		llm_paste=llm_abbr_instructions+' '+names_and_abbr+'.\n'

		for n in c.most_common():
			if n[1]>1:
				prompt=prompt+f'Please differentiate the abbreviations {lang} term "{n[0]}".  An automatic translation tool provided this name for {n[1]} headings:"'

				az=[i['Azimuth'] for i in langCompass if n[0]==i['Abbreviation']]
				names=[i['Heading'] for i in langCompass if n[0]==i['Abbreviation']]

				if not (len(az)==2 and 0 in az and 360 in az): #this is North, it's expected to be duplicated
					print(n[0],az)
					for h,n in zip(az,names):
						h_en=Compass(h)
						prompt=prompt+f'{h}° (in {lang} {n}, in English "{h_en}"), '
		
					llm_paste=llm_paste+prompt[:-2]+'. '
		print(llm_paste)

		raise e

	#wrap around test, per language
	assert langCompass[0]['Heading'] == langCompass[-1]['Heading'], 'Wrap around test fail: Heading'
	assert langCompass[0]['Abbreviation'] == langCompass[-1]['Abbreviation'], 'Wrap around test fail: Abbreviation'
	assert langCompass[0]['Order'] == langCompass[-1]['Order'], 'Wrap around test fail: Order'
	assert langCompass[0]['Azimuth'] < langCompass[-1]['Azimuth'], 'Wrap around test fail: Azimuth'
	print('Pass')


print ('All multilanguage support tests have passed')