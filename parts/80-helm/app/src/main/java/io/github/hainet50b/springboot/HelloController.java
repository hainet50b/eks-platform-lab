package io.github.hainet50b.springboot;

import java.net.InetAddress;
import java.net.UnknownHostException;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
class HelloController {

    @GetMapping("/")
    String hello() {
        return "Hello from Spring Boot\n";
    }

    // In a pod, the host name is the name of the pod.
    @GetMapping("/pod")
    String pod() throws UnknownHostException {
        return InetAddress.getLocalHost().getHostName() + "\n";
    }

}
