async def spare(x_dist, y_dist, z_dist, drone):   #need to check it i think its not work

    dist = sqrt(x_dist ** 2 + y_dist ** 2 + z_dist ** 2)
    x_local, y_local, z_local = await geodetic_to_cartesian_ned(drone)
    local_dist = sqrt(x_local ** 2 + y_local ** 2 + z_local ** 2)
    accuracy = dist - local_dist

    if accuracy < 0.1:
        return 1
    else:
        await asyncio.sleep(0.5)
        return await spare(x_dist, y_dist, z_dist, drone)
