#include <stdbool.h>
#include <stddef.h>

#include <cpuinfo.h>
#include <cpuinfo/internal-api.h>
#include <cpuinfo/log.h>

#ifdef __linux__
#include <linux/api.h>

#include <sys/syscall.h>
#include <unistd.h>
#if !defined(__NR_getcpu)
#include <asm-generic/unistd.h>
#endif
#endif

bool cpuinfo_is_initialized = false;

struct cpuinfo_processor* cpuinfo_processors = NULL;
struct cpuinfo_core* cpuinfo_cores = NULL;
struct cpuinfo_cluster* cpuinfo_clusters = NULL;
struct cpuinfo_package* cpuinfo_packages = NULL;
struct cpuinfo_cache* cpuinfo_cache[cpuinfo_cache_level_max] = {NULL};

uint32_t cpuinfo_processors_count = 0;
uint32_t cpuinfo_cores_count = 0;
uint32_t cpuinfo_clusters_count = 0;
uint32_t cpuinfo_packages_count = 0;
uint32_t cpuinfo_cache_count[cpuinfo_cache_level_max] = {0};
uint32_t cpuinfo_max_cache_size = 0;

#if CPUINFO_ARCH_ARM || CPUINFO_ARCH_ARM64 || CPUINFO_ARCH_RISCV32 || CPUINFO_ARCH_RISCV64
struct cpuinfo_uarch_info* cpuinfo_uarchs = NULL;
uint32_t cpuinfo_uarchs_count = 0;
#else
struct cpuinfo_uarch_info cpuinfo_global_uarch = {cpuinfo_uarch_unknown};
#endif

#ifdef __linux__
uint32_t cpuinfo_linux_cpu_max = 0;
const struct cpuinfo_processor** cpuinfo_linux_cpu_to_processor_map = NULL;
const struct cpuinfo_core** cpuinfo_linux_cpu_to_core_map = NULL;
#if CPUINFO_ARCH_ARM || CPUINFO_ARCH_ARM64 || CPUINFO_ARCH_RISCV32 || CPUINFO_ARCH_RISCV64
const uint32_t* cpuinfo_linux_cpu_to_uarch_index_map = NULL;
#endif
#endif

const struct cpuinfo_processor* cpuinfo_get_processors(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "processors");
	}
	return cpuinfo_processors;
}

const struct cpuinfo_core* cpuinfo_get_cores(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "core");
	}
	return cpuinfo_cores;
}

const struct cpuinfo_cluster* cpuinfo_get_clusters(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "clusters");
	}
	return cpuinfo_clusters;
}

const struct cpuinfo_package* cpuinfo_get_packages(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "packages");
	}
	return cpuinfo_packages;
}

const struct cpuinfo_uarch_info* cpuinfo_get_uarchs() {
	if (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "uarchs");
	}
#if CPUINFO_ARCH_ARM || CPUINFO_ARCH_ARM64 || CPUINFO_ARCH_RISCV32 || CPUINFO_ARCH_RISCV64
	return cpuinfo_uarchs;
#else
	return &cpuinfo_global_uarch;
#endif
}

const struct cpuinfo_processor* cpuinfo_get_processor(uint32_t index) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "processor");
	}
	if CPUINFO_UNLIKELY (index >= cpuinfo_processors_count) {
		return NULL;
	}
	return &cpuinfo_processors[index];
}

const struct cpuinfo_core* cpuinfo_get_core(uint32_t index) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "core");
	}
	if CPUINFO_UNLIKELY (index >= cpuinfo_cores_count) {
		return NULL;
	}
	return &cpuinfo_cores[index];
}

const struct cpuinfo_cluster* cpuinfo_get_cluster(uint32_t index) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "cluster");
	}
	if CPUINFO_UNLIKELY (index >= cpuinfo_clusters_count) {
		return NULL;
	}
	return &cpuinfo_clusters[index];
}

const struct cpuinfo_package* cpuinfo_get_package(uint32_t index) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "package");
	}
	if CPUINFO_UNLIKELY (index >= cpuinfo_packages_count) {
		return NULL;
	}
	return &cpuinfo_packages[index];
}

const struct cpuinfo_uarch_info* cpuinfo_get_uarch(uint32_t index) {
	if (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "uarch");
	}
#if CPUINFO_ARCH_ARM || CPUINFO_ARCH_ARM64 || CPUINFO_ARCH_RISCV32 || CPUINFO_ARCH_RISCV64
	if CPUINFO_UNLIKELY (index >= cpuinfo_uarchs_count) {
		return NULL;
	}
	return &cpuinfo_uarchs[index];
#else
	if CPUINFO_UNLIKELY (index != 0) {
		return NULL;
	}
	return &cpuinfo_global_uarch;
#endif
}

uint32_t cpuinfo_get_processors_count(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "processors_count");
	}
	return cpuinfo_processors_count;
}

uint32_t cpuinfo_get_cores_count(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "cores_count");
	}
	return cpuinfo_cores_count;
}

uint32_t cpuinfo_get_clusters_count(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "clusters_count");
	}
	return cpuinfo_clusters_count;
}

uint32_t cpuinfo_get_packages_count(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "packages_count");
	}
	return cpuinfo_packages_count;
}

uint32_t cpuinfo_get_uarchs_count(void) {
	if (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "uarchs_count");
	}
#if CPUINFO_ARCH_ARM || CPUINFO_ARCH_ARM64 || CPUINFO_ARCH_RISCV32 || CPUINFO_ARCH_RISCV64
	return cpuinfo_uarchs_count;
#else
	return 1;
#endif
}

const struct cpuinfo_cache* CPUINFO_ABI cpuinfo_get_l1i_caches(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l1i_caches");
	}
	return cpuinfo_cache[cpuinfo_cache_level_1i];
}

const struct cpuinfo_cache* CPUINFO_ABI cpuinfo_get_l1d_caches(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l1d_caches");
	}
	return cpuinfo_cache[cpuinfo_cache_level_1d];
}

const struct cpuinfo_cache* CPUINFO_ABI cpuinfo_get_l2_caches(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l2_caches");
	}
	return cpuinfo_cache[cpuinfo_cache_level_2];
}

const struct cpuinfo_cache* CPUINFO_ABI cpuinfo_get_l3_caches(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l3_caches");
	}
	return cpuinfo_cache[cpuinfo_cache_level_3];
}

const struct cpuinfo_cache* CPUINFO_ABI cpuinfo_get_l4_caches(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l4_caches");
	}
	return cpuinfo_cache[cpuinfo_cache_level_4];
}

const struct cpuinfo_cache* CPUINFO_ABI cpuinfo_get_l1i_cache(uint32_t index) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l1i_cache");
	}
	if CPUINFO_UNLIKELY (index >= cpuinfo_cache_count[cpuinfo_cache_level_1i]) {
		return NULL;
	}
	return &cpuinfo_cache[cpuinfo_cache_level_1i][index];
}

const struct cpuinfo_cache* CPUINFO_ABI cpuinfo_get_l1d_cache(uint32_t index) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l1d_cache");
	}
	if CPUINFO_UNLIKELY (index >= cpuinfo_cache_count[cpuinfo_cache_level_1d]) {
		return NULL;
	}
	return &cpuinfo_cache[cpuinfo_cache_level_1d][index];
}

const struct cpuinfo_cache* CPUINFO_ABI cpuinfo_get_l2_cache(uint32_t index) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l2_cache");
	}
	if CPUINFO_UNLIKELY (index >= cpuinfo_cache_count[cpuinfo_cache_level_2]) {
		return NULL;
	}
	return &cpuinfo_cache[cpuinfo_cache_level_2][index];
}

const struct cpuinfo_cache* CPUINFO_ABI cpuinfo_get_l3_cache(uint32_t index) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l3_cache");
	}
	if CPUINFO_UNLIKELY (index >= cpuinfo_cache_count[cpuinfo_cache_level_3]) {
		return NULL;
	}
	return &cpuinfo_cache[cpuinfo_cache_level_3][index];
}

const struct cpuinfo_cache* CPUINFO_ABI cpuinfo_get_l4_cache(uint32_t index) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l4_cache");
	}
	if CPUINFO_UNLIKELY (index >= cpuinfo_cache_count[cpuinfo_cache_level_4]) {
		return NULL;
	}
	return &cpuinfo_cache[cpuinfo_cache_level_4][index];
}

uint32_t CPUINFO_ABI cpuinfo_get_l1i_caches_count(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l1i_caches_count");
	}
	return cpuinfo_cache_count[cpuinfo_cache_level_1i];
}

uint32_t CPUINFO_ABI cpuinfo_get_l1d_caches_count(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l1d_caches_count");
	}
	return cpuinfo_cache_count[cpuinfo_cache_level_1d];
}

uint32_t CPUINFO_ABI cpuinfo_get_l2_caches_count(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l2_caches_count");
	}
	return cpuinfo_cache_count[cpuinfo_cache_level_2];
}

uint32_t CPUINFO_ABI cpuinfo_get_l3_caches_count(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l3_caches_count");
	}
	return cpuinfo_cache_count[cpuinfo_cache_level_3];
}

uint32_t CPUINFO_ABI cpuinfo_get_l4_caches_count(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "l4_caches_count");
	}
	return cpuinfo_cache_count[cpuinfo_cache_level_4];
}

uint32_t CPUINFO_ABI cpuinfo_get_max_cache_size(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "max_cache_size");
	}
	return cpuinfo_max_cache_size;
}

const struct cpuinfo_processor* CPUINFO_ABI cpuinfo_get_current_processor(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "current_processor");
	}
#ifdef __linux__
	/* Initializing this variable silences a MemorySanitizer error. */
	unsigned cpu = 0;
	if CPUINFO_UNLIKELY (syscall(__NR_getcpu, &cpu, NULL, NULL) != 0) {
		return 0;
	}
	if CPUINFO_UNLIKELY ((uint32_t)cpu >= cpuinfo_linux_cpu_max) {
		return 0;
	}
	return cpuinfo_linux_cpu_to_processor_map[cpu];
#else
	return NULL;
#endif
}

const struct cpuinfo_core* CPUINFO_ABI cpuinfo_get_current_core(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "current_core");
	}
#ifdef __linux__
	/* Initializing this variable silences a MemorySanitizer error. */
	unsigned cpu = 0;
	if CPUINFO_UNLIKELY (syscall(__NR_getcpu, &cpu, NULL, NULL) != 0) {
		return 0;
	}
	if CPUINFO_UNLIKELY ((uint32_t)cpu >= cpuinfo_linux_cpu_max) {
		return 0;
	}
	return cpuinfo_linux_cpu_to_core_map[cpu];
#else
	return NULL;
#endif
}

uint32_t CPUINFO_ABI cpuinfo_get_current_uarch_index(void) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal("cpuinfo_get_%s called before cpuinfo is initialized", "current_uarch_index");
	}
#if CPUINFO_ARCH_ARM || CPUINFO_ARCH_ARM64 || CPUINFO_ARCH_RISCV32 || CPUINFO_ARCH_RISCV64
#ifdef __linux__
	if (cpuinfo_linux_cpu_to_uarch_index_map == NULL) {
		/* Special case: avoid syscall on systems with only a single
		 * type of cores
		 */
		return 0;
	}

	/* General case */
	/* Initializing this variable silences a MemorySanitizer error. */
	unsigned cpu = 0;
	if CPUINFO_UNLIKELY (syscall(__NR_getcpu, &cpu, NULL, NULL) != 0) {
		return 0;
	}
	if CPUINFO_UNLIKELY ((uint32_t)cpu >= cpuinfo_linux_cpu_max) {
		return 0;
	}
	return cpuinfo_linux_cpu_to_uarch_index_map[cpu];
#else
	/* Fallback: pretend to be on the big core. */
	return 0;
#endif
#else
	/* Only ARM/ARM64/RISCV processors may include cores of different types
	 * in the same package. */
	return 0;
#endif
}

uint32_t CPUINFO_ABI cpuinfo_get_current_uarch_index_with_default(uint32_t default_uarch_index) {
	if CPUINFO_UNLIKELY (!cpuinfo_is_initialized) {
		cpuinfo_log_fatal(
			"cpuinfo_get_%s called before cpuinfo is initialized", "current_uarch_index_with_default");
	}
#if CPUINFO_ARCH_ARM || CPUINFO_ARCH_ARM64 || CPUINFO_ARCH_RISCV32 || CPUINFO_ARCH_RISCV64
#ifdef __linux__
	if (cpuinfo_linux_cpu_to_uarch_index_map == NULL) {
		/* Special case: avoid syscall on systems with only a single
		 * type of cores
		 */
		return 0;
	}

	/* General case */
	/* Initializing this variable silences a MemorySanitizer error. */
	unsigned cpu = 0;
	if CPUINFO_UNLIKELY (syscall(__NR_getcpu, &cpu, NULL, NULL) != 0) {
		return default_uarch_index;
	}
	if CPUINFO_UNLIKELY ((uint32_t)cpu >= cpuinfo_linux_cpu_max) {
		return default_uarch_index;
	}
	return cpuinfo_linux_cpu_to_uarch_index_map[cpu];
#else
	/* Fallback: no API to query current core, use default uarch index. */
	return default_uarch_index;
#endif
#else
	/* Only ARM/ARM64/RISCV processors may include cores of different types
	 * in the same package. */
	return 0;
#endif
}

const char* CPUINFO_ABI cpuinfo_vendor_to_string(enum cpuinfo_vendor vendor) {
	switch (vendor) {
		case cpuinfo_vendor_unknown:
			return "unknown";
		case cpuinfo_vendor_intel:
			return "Intel";
		case cpuinfo_vendor_amd:
			return "AMD";
		case cpuinfo_vendor_huawei:
			return "Huawei";
		case cpuinfo_vendor_hygon:
			return "Hygon";
		case cpuinfo_vendor_arm:
			return "ARM";
		case cpuinfo_vendor_qualcomm:
			return "Qualcomm";
		case cpuinfo_vendor_apple:
			return "Apple";
		case cpuinfo_vendor_samsung:
			return "Samsung";
		case cpuinfo_vendor_nvidia:
			return "Nvidia";
		case cpuinfo_vendor_mips:
			return "MIPS";
		case cpuinfo_vendor_ibm:
			return "IBM";
		case cpuinfo_vendor_ingenic:
			return "Ingenic";
		case cpuinfo_vendor_via:
			return "VIA";
		case cpuinfo_vendor_cavium:
			return "Cavium";
		case cpuinfo_vendor_broadcom:
			return "Broadcom";
		case cpuinfo_vendor_apm:
			return "Applied Micro";
		default:
			return NULL;
	}
}

const char* CPUINFO_ABI cpuinfo_uarch_to_string(enum cpuinfo_uarch uarch) {
	switch (uarch) {
		case cpuinfo_uarch_unknown:
			return "unknown";
		case cpuinfo_uarch_p5:
			return "P5";
		case cpuinfo_uarch_quark:
			return "Quark";
		case cpuinfo_uarch_p6:
			return "P6";
		case cpuinfo_uarch_dothan:
			return "Dothan";
		case cpuinfo_uarch_yonah:
			return "Yonah";
		case cpuinfo_uarch_conroe:
			return "Conroe";
		case cpuinfo_uarch_penryn:
			return "Penryn";
		case cpuinfo_uarch_nehalem:
			return "Nehalem";
		case cpuinfo_uarch_sandy_bridge:
			return "Sandy Bridge";
		case cpuinfo_uarch_ivy_bridge:
			return "Ivy Bridge";
		case cpuinfo_uarch_haswell:
			return "Haswell";
		case cpuinfo_uarch_broadwell:
			return "Broadwell";
		case cpuinfo_uarch_sky_lake:
			return "Sky Lake";
		case cpuinfo_uarch_palm_cove:
			return "Palm Cove";
		case cpuinfo_uarch_sunny_cove:
			return "Sunny Cove";
		case cpuinfo_uarch_willow_cove:
			return "Willow Cove";
		case cpuinfo_uarch_willamette:
			return "Willamette";
		case cpuinfo_uarch_prescott:
			return "Prescott";
		case cpuinfo_uarch_bonnell:
			return "Bonnell";
		case cpuinfo_uarch_saltwell:
			return "Saltwell";
		case cpuinfo_uarch_silvermont:
			return "Silvermont";
		case cpuinfo_uarch_gracemont:
			return "Gracemont";
		case cpuinfo_uarch_crestmont:
			return "Crestmont";
		case cpuinfo_uarch_airmont:
			return "Airmont";
		case cpuinfo_uarch_goldmont:
			return "Goldmont";
		case cpuinfo_uarch_goldmont_plus:
			return "Goldmont Plus";
		case cpuinfo_uarch_darkmont:
			return "Darkmont";
		case cpuinfo_uarch_knights_ferry:
			return "Knights Ferry";
		case cpuinfo_uarch_knights_corner:
			return "Knights Corner";
		case cpuinfo_uarch_knights_landing:
			return "Knights Landing";
		case cpuinfo_uarch_knights_hill:
			return "Knights Hill";
		case cpuinfo_uarch_knights_mill:
			return "Knights Mill";
		case cpuinfo_uarch_k5:
			return "K5";
		case cpuinfo_uarch_k6:
			return "K6";
		case cpuinfo_uarch_k7:
			return "K7";
		case cpuinfo_uarch_k8:
			return "K8";
		case cpuinfo_uarch_k10:
			return "K10";
		case cpuinfo_uarch_bulldozer:
			return "Bulldozer";
		case cpuinfo_uarch_piledriver:
			return "Piledriver";
		case cpuinfo_uarch_steamroller:
			return "Steamroller";
		case cpuinfo_uarch_excavator:
			return "Excavator";
		case cpuinfo_uarch_zen:
			return "Zen";
		case cpuinfo_uarch_zen2:
			return "Zen 2";
		case cpuinfo_uarch_zen3:
			return "Zen 3";
		case cpuinfo_uarch_zen4:
			return "Zen 4";
		case cpuinfo_uarch_zen5:
			return "Zen 5";
		case cpuinfo_uarch_geode:
			return "Geode";
		case cpuinfo_uarch_bobcat:
			return "Bobcat";
		case cpuinfo_uarch_jaguar:
			return "Jaguar";
		case cpuinfo_uarch_puma:
			return "Puma";
		case cpuinfo_uarch_xscale:
			return "XScale";
		case cpuinfo_uarch_arm7:
			return "ARM7";
		case cpuinfo_uarch_arm9:
			return "ARM9";
		case cpuinfo_uarch_arm11:
			return "ARM11";
		case cpuinfo_uarch_cortex_a5:
			return "Cortex-A5";
		case cpuinfo_uarch_cortex_a7:
			return "Cortex-A7";
		case cpuinfo_uarch_cortex_a8:
			return "Cortex-A8";
		case cpuinfo_uarch_cortex_a9:
			return "Cortex-A9";
		case cpuinfo_uarch_cortex_a12:
			return "Cortex-A12";
		case cpuinfo_uarch_cortex_a15:
			return "Cortex-A15";
		case cpuinfo_uarch_cortex_a17:
			return "Cortex-A17";
		case cpuinfo_uarch_cortex_a32:
			return "Cortex-A32";
		case cpuinfo_uarch_cortex_a35:
			return "Cortex-A35";
		case cpuinfo_uarch_cortex_a53:
			return "Cortex-A53";
		case cpuinfo_uarch_cortex_a55r0:
			return "Cortex-A55r0";
		case cpuinfo_uarch_cortex_a55:
			return "Cortex-A55";
		case cpuinfo_uarch_cortex_a57:
			return "Cortex-A57";
		case cpuinfo_uarch_cortex_a65:
			return "Cortex-A65";
		case cpuinfo_uarch_cortex_a72:
			return "Cortex-A72";
		case cpuinfo_uarch_cortex_a73:
			return "Cortex-A73";
		case cpuinfo_uarch_cortex_a75:
			return "Cortex-A75";
		case cpuinfo_uarch_cortex_a76:
			return "Cortex-A76";
		case cpuinfo_uarch_cortex_a77:
			return "Cortex-A77";
		case cpuinfo_uarch_cortex_a78:
			return "Cortex-A78";
		case cpuinfo_uarch_cortex_a510:
			return "Cortex-A510";
		case cpuinfo_uarch_cortex_a710:
			return "Cortex-A710";
		case cpuinfo_uarch_cortex_a715:
			return "Cortex-A715";
		case cpuinfo_uarch_cortex_x1:
			return "Cortex-X1";
		case cpuinfo_uarch_cortex_x2:
			return "Cortex-X2";
		case cpuinfo_uarch_cortex_x3:
			return "Cortex-X3";
		case cpuinfo_uarch_neoverse_n1:
			return "Neoverse N1";
		case cpuinfo_uarch_neoverse_e1:
			return "Neoverse E1";
		case cpuinfo_uarch_neoverse_v1:
			return "Neoverse V1";
		case cpuinfo_uarch_neoverse_n2:
			return "Neoverse N2";
		case cpuinfo_uarch_neoverse_v2:
			return "Neoverse V2";
		case cpuinfo_uarch_scorpion:
			return "Scorpion";
		case cpuinfo_uarch_krait:
			return "Krait";
		case cpuinfo_uarch_kryo:
			return "Kryo";
		case cpuinfo_uarch_falkor:
			return "Falkor";
		case cpuinfo_uarch_saphira:
			return "Saphira";
		case cpuinfo_uarch_oryon:
			return "Oryon";
		case cpuinfo_uarch_denver:
			return "Denver";
		case cpuinfo_uarch_denver2:
			return "Denver 2";
		case cpuinfo_uarch_carmel:
			return "Carmel";
		case cpuinfo_uarch_exynos_m1:
			return "Exynos M1";
		case cpuinfo_uarch_exynos_m2:
			return "Exynos M2";
		case cpuinfo_uarch_exynos_m3:
			return "Exynos M3";
		case cpuinfo_uarch_exynos_m4:
			return "Exynos M4";
		case cpuinfo_uarch_exynos_m5:
			return "Exynos M5";
		case cpuinfo_uarch_swift:
			return "Swift";
		case cpuinfo_uarch_cyclone:
			return "Cyclone";
		case cpuinfo_uarch_typhoon:
			return "Typhoon";
		case cpuinfo_uarch_twister:
			return "Twister";
		case cpuinfo_uarch_hurricane:
			return "Hurricane";
		case cpuinfo_uarch_monsoon:
			return "Monsoon";
		case cpuinfo_uarch_mistral:
			return "Mistral";
		case cpuinfo_uarch_vortex:
			return "Vortex";
		case cpuinfo_uarch_tempest:
			return "Tempest";
		case cpuinfo_uarch_lightning:
			return "Lightning";
		case cpuinfo_uarch_thunder:
			return "Thunder";
		case cpuinfo_uarch_firestorm:
			return "Firestorm";
		case cpuinfo_uarch_icestorm:
			return "Icestorm";
		case cpuinfo_uarch_avalanche:
			return "Avalanche";
		case cpuinfo_uarch_blizzard:
			return "Blizzard";
		case cpuinfo_uarch_everest:
			return "Everest";
		case cpuinfo_uarch_sawtooth:
			return "Sawtooth";
		case cpuinfo_uarch_coll_everest:
			return "Coll_Everest";
		case cpuinfo_uarch_coll_sawtooth:
			return "Coll_Sawtooth";
		case cpuinfo_uarch_tupai_everest:
			return "Tupai_Everest";
		case cpuinfo_uarch_tupai_sawtooth:
			return "Tupai_Sawtooth";
		case cpuinfo_uarch_tahiti_everest:
			return "Tahiti_Everest";
		case cpuinfo_uarch_tahiti_sawtooth:
			return "Tahiti_Sawtooth";
		case cpuinfo_uarch_brava_pcore:
			return "Brava_PCore";
		case cpuinfo_uarch_brava_ecore:
			return "Brava_ECore";
		case cpuinfo_uarch_thunderx:
			return "ThunderX";
		case cpuinfo_uarch_thunderx2:
			return "ThunderX2";
		case cpuinfo_uarch_pj4:
			return "PJ4";
		case cpuinfo_uarch_brahma_b15:
			return "Brahma B15";
		case cpuinfo_uarch_brahma_b53:
			return "Brahma B53";
		case cpuinfo_uarch_xgene:
			return "X-Gene";
		case cpuinfo_uarch_dhyana:
			return "Dhyana";
		case cpuinfo_uarch_taishan_v110:
			return "TaiShan v110";
		default:
			return NULL;
	}
}
