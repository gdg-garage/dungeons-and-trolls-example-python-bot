rm -rf dungeons_and_trolls_generated_client

docker-compose run client-gen

chmod -R a+rw dungeons_and_trolls_generated_client