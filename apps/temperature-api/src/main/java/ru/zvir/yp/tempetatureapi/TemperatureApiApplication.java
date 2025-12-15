package ru.zvir.yp.tempetatureapi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RequestMapping;

@SpringBootApplication
public class TemperatureApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(TemperatureApiApplication.class, args);
    }

}
