package ru.zvir.yp.tempetatureapi;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/temperature")
public class TemperatureApiController {

    @GetMapping()
    public String getTemperatureByLocation(@RequestParam("location") String location) {
        return switch (location) {
            case "Living Room" -> "1";
            case "Bedroom" -> "2";
            case "Kitchen" -> "3";
            default -> "0";
        };
    }

    @GetMapping("/{sensorId}")
    public String getTemperatureBySensorID(@PathVariable("sensorId") String sensorId) {
        return switch (sensorId) {
            case "1" -> "Living Room";
            case "2" -> "Bedroom";
            case "3" -> "Kitchen";
            default -> "Unknown";
        };
    }
}

