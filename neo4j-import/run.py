from dotenv import load_dotenv
import os
import sys
import re
from neo4j import GraphDatabase
from difflib import SequenceMatcher

load_dotenv()

# database setting
uri = os.environ.get('NEO4J_URL', 'bolt://localhost')
username = os.environ.get('NEO4J_USERNAME', 'neo4j')
password = os.environ.get('NEO4J_PASSWORD', 'neo4j')

countries = [
  "afghanistan", "ålandislands", "albania", "algeria", "americansamoa", "andorra", "angola",
  "anguilla", "antarctica", "antiguaandbarbuda", "argentina", "armenia", "aruba", "australia",
  "austria", "azerbaijan", "bahamas", "bahrain", "bangladesh", "barbados", "belarus", "belgium",
  "belize", "benin", "bermuda", "bhutan", "bolivia", "bosniaandherzegovina", "botswana", "bouvetisland",
  "brazil", "britishindianoceanterritory", "bruneidarussalam", "bulgaria", "burkinafaso", "burundi",
  "cambodia", "cameroon", "canada", "capeverde", "caymanislands", "centralafricanrepublic", "chad",
  "chile", "china", "christmasisland", "cocos(keeling)islands", "colombia", "comoros", "congo",
  "congo,thedemocraticrepublicofthe", "cookislands", "costarica", "cotedivoire", "croatia", "cuba",
  "cyprus", "czechrepublic", "denmark", "djibouti", "dominica", "dominicanrepublic", "ecuador", "egypt",
  "elsalvador", "equatorialguinea", "eritrea", "estonia", "ethiopia", "falklandislands(malvinas)",
  "faroeislands", "fiji", "finland", "france", "frenchguiana", "frenchpolynesia", "frenchsouthernterritories",
  "gabon", "gambia", "georgia", "germany", "ghana", "gibraltar", "greece", "greenland", "grenada", "guadeloupe",
  "guam", "guatemala", "guernsey", "guinea", "guinea-bissau", "guyana", "haiti", "heardislandandmcdonaldislands",
  "holysee(vaticancitystate)", "honduras", "hongkong", "hungary", "iceland", "india", "indonesia", "iran,islamicrepublicof",
  "iraq", "ireland", "isleofman", "israel", "italy", "jamaica", "japan", "jersey", "jordan", "kazakhstan", "kenya",
  "kiribati", "korea,democraticpeople'srepublicof", "korea,republicof", "kuwait", "kyrgyzstan", "laopeople'sdemocraticrepublic",
  "latvia", "lebanon", "lesotho", "liberia", "libyanarabjamahiriya", "liechtenstein", "lithuania", "luxembourg",
  "macao", "macedonia,theformeryugoslavrepublicof", "madagascar", "malawi", "malaysia", "maldives", "mali",
  "malta", "marshallislands", "martinique", "mauritania", "mauritius", "mayotte", "mexico", "micronesia,federatedstatesof",
  "moldova,republicof", "monaco", "mongolia", "montserrat", "morocco", "mozambique", "myanmar", "namibia", "nauru",
  "nepal", "netherlands", "netherlandsantilles", "newcaledonia", "newzealand", "nicaragua", "niger", "nigeria",
  "niue", "norfolkisland", "northernmarianaislands", "norway", "oman", "pakistan", "palau", "palestinianterritory,occupied",
  "panama", "papuanewguinea", "paraguay", "peru", "philippines", "pitcairn", "poland", "portugal", "puertorico",
  "qatar", "reunion", "romania", "russianfederation", "rwanda", "sainthelena", "saintkittsandnevis", "saintlucia",
  "saintpierreandmiquelon", "saintvincentandthegrenadines", "samoa", "sanmarino", "saotomeandprincipe", "saudiarabia",
  "senegal", "serbiaandmontenegro", "seychelles", "sierraleone", "singapore", "slovakia", "slovenia", "solomonislands",
  "somalia", "southafrica", "southgeorgiaandthesouthsandwichislands", "spain", "srilanka", "sudan", "surisvalbardandjanmayen",
  "swaziland", "sweden", "switzerland", "syrianarabrepublic", "taiwan,provinceofchina", "tajikistan", "tanzania,unitedrepublicof",
  "thailand", "timor-leste", "togo", "tokelau", "tonga", "trinidadandtobago", "tunisia", "turkey", "turkmenistan", "turksandcaicosislands",
  "tuvalu", "uganda", "ukraine", "unitedarabemirates", "unitedkingdom", "unitedstates", "unitedstatesminoroutlyingislands", "uruguay",
  "uzbekistan", "vanuatu", "venezuela", "vietnam", "virginislands,british", "virginislands,u.s.", "wallisandfutuna", "westernsahara",
  "yemen", "zambia", "zimbabwe"
]

sub_types = ["H3N2", "H5N1", "H1N1"]

STRAIN_INDEX = 'strainIdIndex'

def similar(a, b):
  return SequenceMatcher(None, a, b).ratio()

def calc_genetic_distance(seq1, seq2):
  if len(seq1) != len(seq2):
    print('GENETIC_DISTANCE: Sequences must have same length for distance calculation.')
    return None

  distance = 0
  for base1, base2 in zip(seq1, seq2):
    if base1 != base2:
      distance += 1
  return distance

def add_strains(tx, strain, key):
  result = tx.run(
    "CREATE (s:Strain {id: $id, sequence: $sequence, type: $type, type_id: $type_id, name: $name, region: $region})",
    id=strain['id'], name=key, sequence=strain['sequence'], type=strain['type'], type_id=strain['type_id'], region=strain['region']
  )
  return result

def add_similarity(tx, id1, id2, similarity):
  result = tx.run(
    "MATCH(s1:Strain {id: $id1}), (s2:Strain {id: $id2}) CREATE (s1)-[:SEQUENCE_SIMILARITY {value: $similarity}]-> (s2)",
    id1=id1, id2=id2, similarity=similarity
  )
  return result

def add_distance(tx, id1, id2, distance):
  result = tx.run(
    "MATCH(s1:Strain {id: $id1}), (s2:Strain {id: $id2}) CREATE (s1)-[:DISTANCE {value: $distance}]-> (s2)",
    id1=id1, id2=id2, distance=distance
  )
  return result

def add_genetic_distance(tx, id1, id2, distance):
  result = tx.run(
    "MATCH(s1:Strain {id: $id1}), (s2:Strain {id: $id2}) CREATE (s1)-[:GENETIC_DISTANCE {value: $distance}]-> (s2)",
    id1=id1, id2=id2, distance=distance
  )
  return result

def add_hi_titer_value(tx, id1, id2, value):
  result = tx.run(
    "MATCH(s1:Strain {id: $id1}), (s2:Strain {id: $id2}) CREATE (s1)-[:HI_TITER_VALUE {value: $value}]-> (s2)",
    id1=id1, id2=id2, value=value
  )
  return result

def build_strain_obj(strain_name, sequence, strain_id, each_type, type_id):
  splited_name = strain_name.split("/")
  region = splited_name[1]
  for country in countries:
    if country in strain_name.replace("_", "").lower():
      region = country

  return {
    "sequence": sequence,
    "id": strain_id,
    "type": each_type,
    "type_id": type_id,
    "region": region.upper()
  }


if __name__ == "__main__":
  print("Converting csv into neo4j...")
  strain_objs = {}
  edges = []
  hi_titer_values = []
  strain_id = 0

  for each_type in sub_types:
    # Process strains data
    strains_file_path = os.path.join(
      os.path.dirname(os.path.abspath(__file__)),
      './data/{}/strains'.format(each_type)
    )
    with open(strains_file_path, 'r') as file:
      file_data = file.read()
      lines = file_data.strip().split('\n')

      sequences = []
      for line in lines:
        parts = line.split()
        if len(parts) == 2:
          strain, sequence = parts
          sequences.append([strain, sequence])

      # Remove "#" characters from sequences
      sequences = [[s.replace("#", ""), seq.replace("#", "")] for s, seq in sequences]

      # Create Strain objects
      for row in sequences:
        strain, sequence = row
        strain_name = '{}/{}'.format(strain, each_type)
        strain_objs[strain_name] = build_strain_obj(
          strain_name,
          sequence,
          strain_id,
          each_type,
          sub_types.index(each_type)
        )
        strain_id += 1

    # Process antigenetic data
    antigenetic_file_path = os.path.join(
      os.path.dirname(os.path.abspath(__file__)),
      './data/{}/antigenetic'.format(each_type)
    )
    with open(antigenetic_file_path, 'r') as file:
      file_data = file.read()
      lines = file_data.strip().split('\n')

      distances = []
      for line in lines:
        parts = line.split()
        if len(parts) == 3:
          strain1, strain2, distance = parts
          distances.append([strain1, strain2, distance])

      # Remove "#" characters from distances
      distances = [[s1.replace("#", ""), s2.replace("#", ""), d] for s1, s2, d in distances]

      min_list = []
      for row in distances:
        strain1, strain2, distance = row
        strain1 = '{}/{}'.format(strain1, each_type)
        strain2 = '{}/{}'.format(strain2, each_type)

        if not strain1 in strain_objs:
          strain_objs[strain1] = build_strain_obj(
            strain1,
            '',
            strain_id,
            each_type,
            sub_types.index(each_type)
          )
          strain_id += 1

        if not strain2 in strain_objs:
          strain_objs[strain2] = build_strain_obj(
            strain2,
            '',
            strain_id,
            each_type,
            sub_types.index(each_type)
          )
          strain_id += 1

        similarity = similar(
          strain_objs[strain1]["sequence"],
          strain_objs[strain2]["sequence"]
        )

        genetic_distance = calc_genetic_distance(
          strain_objs[strain1]["sequence"],
          strain_objs[strain2]["sequence"]
        )

        edges.append([
          strain_objs[strain1]["id"],
          strain_objs[strain2]["id"],
          float(distance),
          similarity,
          genetic_distance
        ])

        if float(distance) <= 4:
          min_list.append(similarity)

      match_count = sum(1 for each in min_list if each >= 0.6)

    # Process hi-titer data
    hi_titer_file_path = os.path.join(
      os.path.dirname(os.path.abspath(__file__)),
      './data/{}/hi-titer'.format(each_type)
    )
    with open(hi_titer_file_path, 'r') as file:
      file_data = file.read()
      lines = file_data.strip().split('\n')

      values = []
      for line in lines:
        parts = line.split()
        if len(parts) == 3:
          strain1, strain2, value = parts
          values.append([strain1, strain2, value])

      # Remove "#" characters from values
      values = [[s1.replace("#", ""), s2.replace("#", ""), v] for s1, s2, v in values]

      min_list = []
      for row in values:
        strain1, strain2, value = row
        strain1 = '{}/{}'.format(strain1, each_type)
        strain2 = '{}/{}'.format(strain2, each_type)

        if not strain1 in strain_objs:
          strain_objs[strain1] = build_strain_obj(
            strain1,
            '',
            strain_id,
            each_type,
            sub_types.index(each_type)
          )
          strain_id += 1

        if not strain2 in strain_objs:
          strain_objs[strain2] = build_strain_obj(
            strain2,
            '',
            strain_id,
            each_type,
            sub_types.index(each_type)
          )
          strain_id += 1

        hi_titer_values.append([
          strain_objs[strain1]["id"],
          strain_objs[strain2]["id"],
          float(value)
        ])

  # start database related stuffs
  driver = GraphDatabase.driver(uri, auth=(username, password))
  session = driver.session()

  print('Dropping existing nodes...')
  session.run('MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r')

  # Drop the index if it exists
  print('Creating index "{}"...'.format(STRAIN_INDEX))
  session.run('DROP INDEX {} IF EXISTS'.format(STRAIN_INDEX))
  # create index
  session.run('CREATE INDEX {} FOR (s:Strain) ON (s.id)'.format(STRAIN_INDEX))

  print('Importing data...')
  for key in strain_objs:
    strain = strain_objs.get(key)
    session.write_transaction(add_strains, strain, key)

  for row in edges:
    id1, id2, distance, similarity, genetic_distance = row
    session.write_transaction(add_similarity, id1, id2, similarity)
    session.write_transaction(add_distance, id1, id2, distance)
    if genetic_distance != None:
      session.write_transaction(add_genetic_distance, id1, id2, genetic_distance)

  for row in hi_titer_values:
    id1, id2, value = row
    session.write_transaction(add_hi_titer_value, id1, id2, value)

  print('Done!')
  # driver.close()
