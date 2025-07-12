#!/bin/bash
#!/bin/bash

echo "Building scanner.go ..."

# Try to build the Go scanner binary
if go build -o scanner scanner.go; then
    echo "Build successful! Scanner binary created: ./scanner"
else
    echo "Build failed! Please check your Go environment and dependencies."
    exit 1
fi

