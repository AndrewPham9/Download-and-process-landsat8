import psycopg2
import configparser

#create a dictionary of parameter using configparser
def config (configFile = 'db.txt', section = 'postgresql'):
	parser = configparser.ConfigParser()
	parser.read(configFile)
	return dict(parser.items(section))

def insertSQL (table,**fieldsValues):
	conn = psycopg2.connect(**config())
	cur = conn.cursor()
	fieldState =str()
	valueState =str()
	for field, value in fieldsValues.items():
		fieldState = fieldState + "%s, "%(field)
		valueState = valueState + "'%s', "%(value)
	state = "INSERT INTO " + table + ' (' + fieldState[0:-2] + ') VALUES (' + valueState[0:-2] + ')'
	cur.execute(state)
	conn.commit()
	conn.close()

def selectAll (table):
	conn = psycopg2.connect(**config())
	cur = conn.cursor()
	cur.execute("SELECT * FROM %s"%(table))
	records = cur.fetchall()
	conn.close()
	return records
	
def selectCol (table, *fields, where):
	conn = psycopg2.connect(**config())
	cur = conn.cursor()
	fieldState =str()
	for field in fields:
		fieldState = fieldState + "%s, "%(field)
	state = 'SELECT ' + fieldState[0:-2] + ' FROM ' + table + ' WHERE ' + where
	cur.execute(state)
	records = cur.fetchall()
	conn.close()
	return records

#usage: update ('hehe',*{a = 1, b = 2}, where = "he = 'him'")
#or: update ('hehe',a = 1, b = 2, where = "he = 'him'")
def update (table,where,**fieldsValues):
	conn = psycopg2.connect(**config())
	cur = conn.cursor()
	fieldValueState = str()
	for field, value in fieldsValues.items():
		fieldValueState = fieldValueState + field + ' = ' + "'%s', " %(value)
	state = 'UPDATE ' + table + ' SET ' + fieldValueState[0:-2] +' WHERE ' + where
	cur.execute(state)
	conn.commit()
	conn.close()

def getGeom(Xmin,Ymin,Xmax,Ymax,Projection):
	conn = psycopg2.connect(**config())
	cur = conn.cursor()
	state = 'SELECT ST_MakeEnvelope('+ str(Xmin) +',' + str(Ymin) +','+ str(Xmax) +','+ str(Ymax) +','+ str(Projection)  +')'
	print (state)
	cur.execute(state)
	records = cur.fetchall()
	conn.close()
	return records[0][0]

