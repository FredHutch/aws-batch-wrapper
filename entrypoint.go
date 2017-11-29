/*
An entrypoint that handles several AWS Batch-related tasks.
*/
package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strconv"
	"syscall"
)

var (
	ebsmountExe string = "echo" // FIXME change this to ebsmount when ready
	wantScratch bool   = false
	// scratchSize int64  = 0
)

// entrypoint of the entrypoint.
func main() {
	// look in env vars to see if user wants scratch space
	// if they do, set it up.

	// in future, we could at this point mount /app
	// (and/or something else) via EBS/EFS if the user
	// indicates they want it via some environment variable.

	// look in env vars to see if user wants fetch and run
	// if so, run it -- don't exit if it errors out but save the error code

	// if they don't want fetch and run, run the 'command' ($@ in bash)
	// again, don't exit on error but save the error

	// if user wanted scratch space, delete those volumes now

	// exit with 0 if all was fine or with saved error code if
	// fetch-and-run or 'command' failed.

	// a somewhat unrelated thing- in job wrapper code,
	// there should be an option to sleep for some period of
	// time between starting jobs. otherwise we could run into
	// RequestLimitExceeded errors when creating volumes

	// exitcode := runcmd("testt", []string{"arg1", "arg2"})
	// fmt.Printf("Exit code was %d.\n", exitcode)

	// output := getCmdOutput("echo", []string{"foobar"})
	// fmt.Printf("Output:\n%s\n", output)
	if os.Getenv("SCRATCH_SIZE") != "" {
		wantScratch = true
		if scratchSize, err := strconv.ParseInt(os.Getenv("SCRATCH_SIZE"),
			10, 64); err != nil {
			fmt.Printf("SCRATCH_SIZE environment variable %s is not a number!\n",
				os.Getenv("SCRATCH_SIZE"))
			os.Exit(1)
		} else {
			fmt.Printf("yay, your scratch size is %d GB.\n", scratchSize)
		}
		// fmt.Printf("yay, your scratch size is %d GB.\n", scratchSize)

	}
}

// Run a command and get its output.
// Exit if the command fails (may change this...)
func getCmdOutput(cmdName string, cmdArgs []string) string {
	out, err := exec.Command(cmdName, cmdArgs...).Output()
	if err != nil {
		log.Fatal(err)
	}
	return string(out[:len(out)])
	// ret := fmt.Printf("%s", out)
	// fmt.Println(ret)
	// return "foo"
}

// Run a command and display its stdout and stderr (combined).
// Errors are ok but the exit code is saved,
// with the expectation that entrypoint will exit with that code
// after it cleans up.
func runcmd(cmdName string, cmdArgs []string) int {
	// docker build current directory
	// cmdName := "testt"
	// cmdArgs := []string{"build", "."}

	log.Printf("Preparing to run %s with arguments %s.\n",
		cmdName, cmdArgs)
	cmd := exec.Command(cmdName, cmdArgs...)
	cmdReader, err := cmd.StdoutPipe()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error creating StdoutPipe for Cmd", err)
		os.Exit(1)
	}
	cmd.Stderr = cmd.Stdout

	scanner := bufio.NewScanner(cmdReader)
	go func() {
		for scanner.Scan() {
			fmt.Printf("%s\n", scanner.Text())
		}
	}()

	err = cmd.Start()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error starting Cmd", err)
		//os.Exit(1)
	}

	err = cmd.Wait()

	if exiterr, ok := err.(*exec.ExitError); ok {
		if status, ok := exiterr.Sys().(syscall.WaitStatus); ok {
			log.Printf("Exit Status: %d", status.ExitStatus())
			return status.ExitStatus()
		}
	} else {
		// log.Fatalf("cmd.Waitttt: %v", err)
		log.Printf("Exit Status: 0")
		return 0
	}

	// if err != nil {
	// 	fmt.Fprintln(os.Stderr, "Error waiting for Cmd", err)
	// 	//os.Exit(1)
	// 	return
	// }
	// return 0
	return -1 // should never get here
}
