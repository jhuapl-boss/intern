import intern
from intern.remote.dvid import DVIDRemote
from intern.resource.dvid.resource import DataInstanceResource
from intern.resource.dvid.resource import RepositoryResource

#DVID Data fetch:
dvid = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8001",
	})

DATA_INSTANCE = 'ex_EM'
ALIAS = "Test_alias"

########### Test Project API ###########
## Create DataInstanceResource and force the creation of a RepositoryResource
instance_setup_em = DataInstanceResource(
    DATA_INSTANCE, None, 'uint8blk',ALIAS, 'Example channel.', datatype='uint8')

# Get the channel and create a project
instance_actual_repo = dvid.create_project(instance_setup_em)
print("Repo UUID:" + instance_actual_repo)

#Create an instance within given repo(UUID)
instance_setup_anno = DataInstanceResource(
	DATA_INSTANCE+"_the_second" , instance_actual_repo, 'uint8blk',ALIAS, 'Example channel.', datatype='uint8')

instance_actual_anno_uuid = dvid.create_project(instance_setup_anno)
print("Data Instance UUID: {}".format(instance_actual_anno_uuid))

# Create a dummy repo with the Repository Resource for deletion
instance_setup_em_delete = RepositoryResource(None, "Test_for_deletion")
instance_actual_em_delete_uuid = dvid.create_project(instance_setup_em_delete)
instance_actual_em_delete = dvid.delete_project(instance_setup_em_delete)
print("Successfully deleted Repo project: {}".format(instance_actual_em_delete_uuid))

# Delete the data instance of a repo
instance_setup_em_delete = DataInstanceResource(
	 DATA_INSTANCE, None, 'uint8blk',ALIAS, 'Example channel.', datatype='uint8')
instance_actual_em_delete_uuid = dvid.create_project(instance_setup_em_delete)
dvid.delete_project(dvid.get_instance(instance_actual_em_delete_uuid, DATA_INSTANCE))
print("Successfully deleted data instance project: {}".format(instance_actual_em_delete_uuid))

########### Test Versioning API ###########
# Set up a new project with a channel

instance_setup_merge = DataInstanceResource(
	DATA_INSTANCE+"_the_second" , None, 'uint8blk',"Mege_repo", 'Example channel.', datatype='uint8')

chan_actual_parent1 = dvid.create_project(instance_setup_merge)
print("\nParent1 UUID: " + chan_actual_parent1)
commit_1 = dvid.commit(chan_actual_parent1, note='Test the commit')
branch_1 = dvid.branch(chan_actual_parent1, note='Test the versioning system once')

branch_2 = dvid.branch(chan_actual_parent1, note='Test the versioning system twice')

print("Created branches {} and {} from Parent1".format(branch_1, branch_2))

########### Test Metadat API ###########
# Set up a new project with a channel
print(dvid.get_info(instance_setup_merge))
print(dvid.get_server_info())
print(dvid.get_server_compiled_types())
print(dvid.server_reload_metadata())

########### Test Voluming API ###########
# 

# Uploading data
# dataU = dvid.create_cutout(chan_setup,"xbrain_port9",0,0,390,"/*.tif")
