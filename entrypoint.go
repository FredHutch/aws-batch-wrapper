/*
An entrypoint that handles several AWS Batch-related tasks.
*/
package main

import (
	"bufio"
	"bytes"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"syscall"
)

var (
	batchitExe = "batchit" // comment this out in testing

// batchitExe = "echo" // comment this out in 'production'
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
	retcode := 0
	defer func() { os.Exit(retcode) }()

	var scratchSize = getenv("SCRATCH_SIZE", "", true)
	var volIds string
	if scratchSize != "" {
		volIds = makeScratchSpace(scratchSize)
		defer tearDownVolumes(volIds)
	}

	if wantFetchAndRun() {
		retcode = runcmd("fetch_and_run.sh", []string{})
	} else {
		argLen := len(os.Args)
		if argLen < 2 {
			fmt.Println("You didn't specify a command! Exiting.")
			retcode = 1
			return
		}
		prog := os.Args[1]
		progArgs := os.Args[2:]
		retcode = runcmd(prog, progArgs)
	}
	fmt.Printf("Exiting with return code %d.\n", retcode)
}

func tearDownVolumes(volIds string) {
	progArgs := strings.Split(volIds, " ")
	resultCode, _ := getCmdOutput(batchitExe, progArgs)
	if resultCode != 0 {
		fmt.Printf("Failed to tear down volumes, exit code %d, exiting.\n", resultCode)
		os.Exit(1)
	}
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
	val, ok := os.LookupEnv(key)
	if !ok {
		val = defaultValue
	}

	if mustBeNumber {
		_, err := strconv.Atoi(val)
		if err != nil {
			if !ok {
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
	retCode, volIds := getCmdOutput(batchitExe, progArgs)
	if retCode != 0 {
		fmt.Printf("ebsmount command failed with error %d, exiting.\n", retCode)
		os.Exit(1)
	}

	return volIds
}

// Run a command and get its output.
// Exit if the command fails (may change this...)
func getCmdOutputOld(cmdName string, cmdArgs []string) string {
	//FIXME need to see full output (stdout and stderr) while returning stdout
	// and if we can do that, we only need 1 function for running commands...
	fmt.Printf("getCmdOutput: cmdName is %s and cmdArgs is %v\n", cmdName, cmdArgs)
	out, err := exec.Command(cmdName, cmdArgs...).Output()
	if err != nil {
		log.Fatal(err)
	}
	ret := string(out[:len(out)])
	fmt.Printf("getCmdOutput: returning %s\n", ret)
	return ret
}

func getCmdOutput(cmdName string, cmdArgs []string) (resultCode int, output string) {
	// docker build current directory
	// cmdName := "testt"
	// cmdArgs := []string{"build", "."}

	var buf bytes.Buffer

	log.Printf("runcmd: Preparing to run %s with arguments %s.\n",
		cmdName, cmdArgs)
	cmd := exec.Command(cmdName, cmdArgs...)
	cmdReader, err := cmd.StdoutPipe()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error creating StdoutPipe for Cmd", err)
		os.Exit(1)
	}
	//cmd.Stderr = cmd.Stdout

	stderrReader, err := cmd.StderrPipe()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error creating StderrPipe for Cmd", err)
		os.Exit(1)
	}

	scanner := bufio.NewScanner(cmdReader)
	go func() {
		for scanner.Scan() {
			fmt.Printf("STDOUT: %s\n", scanner.Text())
			buf.WriteString(scanner.Text())
			buf.WriteString("\n")
		}
	}()

	scannerStderr := bufio.NewScanner(stderrReader)
	go func() {
		for scannerStderr.Scan() {
			fmt.Printf("STDERR: %s\n", scannerStderr.Text())
		}
	}()

	err = cmd.Start()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error starting Cmd", err)
		//os.Exit(1)
	}

	err = cmd.Wait()
	output = strings.TrimSuffix(buf.String(), "\n")

	if exiterr, ok := err.(*exec.ExitError); ok {
		if status, ok := exiterr.Sys().(syscall.WaitStatus); ok {
			log.Printf("Exit Status: %d", status.ExitStatus())
			return status.ExitStatus(), output
		}
	} else {
		log.Printf("Exit Status: 0")
		return 0, output
	}

	return -1, output // should never get here
}

// Run a command and display its stdout and stderr (combined).
// Errors are ok but the exit code is saved,
// with the expectation that entrypoint will exit with that code
// after it cleans up.
func runcmd(cmdName string, cmdArgs []string) int {
	// docker build current directory
	// cmdName := "testt"
	// cmdArgs := []string{"build", "."}

	log.Printf("runcmd: Preparing to run %s with arguments %s.\n",
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
		log.Printf("Exit Status: 0")
		return 0
	}

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
