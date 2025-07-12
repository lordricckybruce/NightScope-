package main

import (
    "fmt"
    "net"
    "os"
    "strconv"
    "sync"
    "time"
)

var commonPorts = map[int]string{
    80:   "HTTP",
    443:  "HTTPS",
    21:   "FTP",
    22:   "SSH",
    25:   "SMTP",
    53:   "DNS",
    110:  "POP3",
    143:  "IMAP",
    3306: "MySQL",
    8080: "HTTP-Alt",
}

func main() {
    if len(os.Args) < 2 {
        fmt.Printf("Usage: %s <target> [max_port]\n", os.Args[0])
        os.Exit(1)
    }

    target := os.Args[1]
    maxPort := 1000
    if len(os.Args) > 2 {
        p, err := strconv.Atoi(os.Args[2])
        if err == nil && p > 0 && p <= 65535 {
            maxPort = p
        }
    }

    fmt.Printf("Scanning target: %s\n", target)
    ips, err := net.LookupIP(target)
    if err != nil {
        fmt.Printf("Error resolving target: %v\n", err)
        os.Exit(1)
    }

    var ipv4s []net.IP
    for _, ip := range ips {
        if ip.To4() != nil {
            ipv4s = append(ipv4s, ip)
        }
    }
    if len(ipv4s) == 0 {
        fmt.Println("No IPv4 address found for target")
        os.Exit(1)
    }

    fmt.Printf("Resolved IPs: %v\n", ipv4s)
    fmt.Printf("Starting TCP Connect scan up to port %d...\n", maxPort)

    openPorts := make(chan int, maxPort)
    var wg sync.WaitGroup
    timeout := 500 * time.Millisecond

    // We'll scan only the first IPv4 resolved IP for simplicity
    ipStr := ipv4s[0].String()

    for port := 1; port <= maxPort; port++ {
        wg.Add(1)
        go func(p int) {
            defer wg.Done()
            address := fmt.Sprintf("%s:%d", ipStr, p)
            conn, err := net.DialTimeout("tcp", address, timeout)
            if err == nil {
                conn.Close()
                openPorts <- p
            }
        }(port)
    }

    go func() {
        wg.Wait()
        close(openPorts)
    }()

    openPortList := []int{}
    for port := range openPorts {
        service := commonPorts[port]
        if service == "" {
            service = "Unknown"
        }
        fmt.Printf("[OPEN] Port %d (%s)\n", port, service)
        openPortList = append(openPortList, port)
    }

    fmt.Printf("Scan complete. Total open ports: %d\n", len(openPortList))
}
