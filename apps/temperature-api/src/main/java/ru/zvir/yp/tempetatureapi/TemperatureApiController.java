package ru.zvir.yp.tempetatureapi;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalTime;
import java.util.concurrent.ThreadLocalRandom;

@RestController
@RequestMapping("/temperature")
public class TemperatureApiController {

    @GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<TemperatureResponse> getTemperatureByLocation(@RequestParam("location") String location) {
        String sensorID = switch (location) {
            case "Living Room" -> "1";
            case "Bedroom" -> "2";
            case "Kitchen" -> "3";
            default -> "0";
        };
        return ResponseEntity.ok(new TemperatureResponse(
                Math.round(ThreadLocalRandom.current().nextDouble(-100, 100) * 100.0) / 100.0,
                "celsius",
                LocalTime.now().toString(),
                location,
                "OK",
                sensorID,
                "temperature",
                "Temperature by location"
        ));

    }

    @GetMapping(value = "/{sensorId}", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<TemperatureResponse> getTemperatureBySensorID(@PathVariable String sensorId) {
        String location = switch (sensorId) {
            case "1" -> "Living Room";
            case "2" -> "Bedroom";
            case "3" -> "Kitchen";
            default -> "Unknown";
        };
        return ResponseEntity.ok(new TemperatureResponse(
                Math.round(ThreadLocalRandom.current().nextDouble(-100, 100) * 100.0) / 100.0,
                "celsius",
                LocalTime.now().toString(),
                location,
                "OK",
                sensorId,
                "temperature",
                "Temperature by location"
        ));
    }
}

