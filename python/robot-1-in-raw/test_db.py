import dbSpectro

db=dbSpectro.init_connection()

alpha='06 37 24.0413'
delta='+06 08 07.371'
print alpha,delta
objId=dbSpectro.getObjId_fromRaDec(db,alpha,delta)

print 'objId=',objId

exit()
