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
	"strings"
	"syscall"
)

var (
	batchitExe = "echo" // FIXME change this to batchit when ready
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

	var scratchSize = getenv("SCRATCH_SIZE", "", true)
	var volIds string
	if scratchSize != "" {
		volIds = makeScratchSpace(scratchSize)
	}

	var retVal int
	if wantFetchAndRun() {
		retVal = runcmd("fetch_and_run.sh", []string{})
	} else {
		prog := os.Args[0]
		progArgs := os.Args[1:]
		retVal = runcmd(prog, progArgs)
	}

	// tear down volumes
	if volIds != "" {
		progArgs := strings.Split(volIds, " ")
		getCmdOutput(batchitExe, progArgs)
	}

	// exit with retVal
	os.Exit(retVal)

}

func wantFetchAndRun() bool {
	vars := []string{"BATCH_FILE_TYPE", "BATCH_FILE_S3_URL"}
	for i := 0; i < 2; i++ {
		if getenv(vars[i], "", false) == "" {
			return false
		}
	}
	return true
}

// Get an environment variable or a default if not set.
func getenv(key string, defaultValue string, mustBeNumber bool) string {
	val := os.Getenv("KEY")
	if val == "" {
		val = defaultValue
	}
	if mustBeNumber {
		_, err := strconv.Atoi(val)
		if err != nil {
			if val != "" {
				fmt.Printf("Warning: %s is not a number, ignoring!\n", val)
			}
			return ""
		}
	}
	return val
}

type ebsMountArgs struct {
	Size       string
	MountPoint string
	VolumeType string
	FSType     string
	Iops       string
	N          string
	Keep       string
}

// Create a scratch volume using batchit
func makeScratchSpace(scratchSize string) string {
	var args ebsMountArgs
	args.Size = scratchSize
	args.MountPoint = "/scratch"
	args.N = "1"
	sz, _ := strconv.Atoi(args.Size) // we already checked that it's a number
	if sz > 200 {
		args.N = "2"
	}

	progArgs := []string{"ebsmount", "--size", args.Size, "--mountpoint",
		args.MountPoint, "-n", args.N}
	volIds := getCmdOutput(batchitExe, progArgs)
	return volIds

}

// Run a command and get its output.
// Exit if the command fails (may change this...)
func getCmdOutput(cmdName string, cmdArgs []string) string {
	fmt.Printf("getCmdOutput: cmdName is %s and cmdArgs is %v", cmdName, cmdArgs)
	out, err := exec.Command(cmdName, cmdArgs...).Output()
	if err != nil {
		log.Fatal(err)
	}
	ret := string(out[:len(out)])
	fmt.Printf("getCmdOutput: returning %s\n", ret)
	return ret
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

// does a list of strings contain a given string?
func contains(haystack []string, needle string) bool {
	for _, h := range haystack {
		if h == needle {
			return true
		}
	}
	return false
}
