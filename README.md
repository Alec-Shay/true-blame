### Prerequisites

### Installation
Clone this repository : 
`git@github.com/alec-shay/true-blame.git`

Add this section to .bash_aliases (or the equivalent on whichever shell you're using) which calls the script.  Ensure /path/to/clone/location is modified to be wherever you've cloned the repository.

```bash
TB_PATH=/path/to/clone/location

tb() {
        ${TB_PATH}/tb $@
}
```

Additionally hook the function tb() to your build / ant-all / gw workflow to always have the hash of your bundle.