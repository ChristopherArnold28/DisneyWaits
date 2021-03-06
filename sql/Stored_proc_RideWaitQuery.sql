DELIMITER $$
CREATE DEFINER=`chrisArnold1228`@`%` PROCEDURE `RideWaitQuery`()
BEGIN

select 
	WaitData.RideId,
    WaitData.Date,
    WaitData.Time,
    WaitData.Wait,
    WaitData.Name,
    WaitData.OpeningDate,
    WaitData.Tier,
    WaitData.Location,
    WaitData.IntellectualProp,
    WaitData.Status,
    WaitData.Temperature,
    WaitData.CloudCover,
    WaitData.SimpleStatus,
    WaitData.RainAccumulation,
    ParkHours.ParkId,
    ParkHours.ParkOpen,
    ParkHours.ParkClose,
    ParkHours.EMHOpen,
    ParkHours.EMHClose,
    Park.Name as ParkName
from(
	select
		Ride_Waits.RideId,
		Ride_Waits.Date,
		Ride_Waits.Time,
		Ride_Waits.Wait,
		Ride.Name,
		Ride.OpeningDate,
		Ride.Tier,
		Ride.Location,
		Ride.ParkId,
        Ride.IntellectualProp,
		Weather.Status,
		Weather.Temperature,
		Weather.CloudCover,
		Weather.SimpleStatus,
		Weather.RainAccumulation
	from
		Ride_Waits
		join Ride on Ride.Id = Ride_Waits.RideId
		join Weather on Weather.Date = Ride_Waits.Date and Weather.Time = Ride_Waits.Time) WaitData
join ParkHours on WaitData.ParkId = ParkHours.ParkId and WaitData.Date = ParkHours.Date
join Park on Park.Id = ParkHours.ParkId;
END$$
DELIMITER ;
