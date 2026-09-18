#########################################################################################
# makefile variables for VLSI benchmarks
#########################################################################################
benchmark ?= none
technology_name ?= nangate45
toolchain ?= commercial

EXTRA_CONFS ?=

ifneq ($(benchmark),none)
    tech_name ?= $(technology_name)
endif 

ifeq ($(benchmark),cva6)
    CONFIG            = CVA6Config
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       =  ./vlsi-cva6
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
    EXTRA_PREPROC_DEFINES ?=SYNTHESIS
endif

ifeq ($(benchmark),boomv3-medium)
    CONFIG            = MediumBoomV3Config
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),boomv4-medium)
    CONFIG            = MediumBoomV4Config
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),gemmini-rocket)
    CONFIG            = GemminiRocketConfig
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),ibex)
    CONFIG            = IbexConfig
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./vlsi-ibex
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
    EXTRA_PREPROC_DEFINES += YOSYS
endif

ifeq ($(benchmark),fft-rocket)
    CONFIG            = FFTRocketConfig
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),shuttle)
    CONFIG            = ShuttleConfig
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),multi-noc)
    CONFIG            = MultiNoCConfig
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),rocket)
    CONFIG            = RocketConfig
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),nvdla)
    CONFIG            = SmallNVDLARocketConfig
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       =  ./vlsi-nvdla
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),rocket-many-peripherals)
    CONFIG            = ManyPeripheralsRocketConfig
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),multisim-llc-chiplet)
    generated_src_name ?= generated-src-$(technology_name)
    CONFIG            ?= MultiSimLLCChipletRocketConfig
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),symmetric-rocket)
    CONFIG            = SymmetricChipletRocketConfig
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),refv-vector-unit)
    CONFIG            = REFV256D128M64RocketConfig
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif

ifeq ($(benchmark),dualrocket)
    CONFIG            = DualRocketConfig
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       = ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif


ifeq ($(benchmark),radiance)
    CONFIG            = RadianceTapeoutSimConfig 
    generated_src_name ?= generated-src-$(technology_name)
    HAMMER_EXEC       =  ./example-vlsi
    TOOLS_CONF        ?= example-tools.yml
    TECH_CONF         ?= ./technology/$(technology_name).yml
    FSIM_CONF_FILE    ?= ./fsim/example-fsim-$(FAULT_MODEL).yml
    DESIGN_CONFS      ?= ./example-designs/$(technology_name)-$(toolchain).yml
    VLSI_OBJ_DIR      ?= build-$(technology_name)-$(toolchain)-$(benchmark)
    INPUT_CONFS       ?= $(TOOLS_CONF) $(TECH_CONF) $(DESIGN_CONFS) $(EXTRA_CONFS)
endif


