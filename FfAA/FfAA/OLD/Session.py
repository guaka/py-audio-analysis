
try:
	import ZODB, ZODB.FileStorage
	from Persistence import Persistent, PersistentMapping
	_ZODB_available = True

	def save():
		get_transaction().commit()

	def close_db():
		save()
		db.close()


	try:
		storage = ZODB.FileStorage.FileStorage(_file_for_storing_structures())
		db = ZODB.DB(storage)
		conn = db.open()
	
		dbroot = conn.root()
		if not dbroot.has_key('structures'):
			print_color (3, "Add structures to database\n")
			dbroot['structures'] = Structures()
		
		structures = dbroot['structures']
		init = Structure_Initializer(structures)
		
		print "structures = dbroot['structures']"
		print "init = Structure_Initializer(structures)"
	
	except ZODB.POSException.StorageSystemError:
		print "Sound Structure database already opened by another process."
		structures = None

except ImportError:
	print "Hmm..."
