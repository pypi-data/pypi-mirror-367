#ifndef NEXUS_RUNTIME_H
#define NEXUS_RUNTIME_H

#include <nexus/device.h>

#include <string>

namespace nexus {

namespace detail {
class RuntimeImpl;
}  // namespace detail

// Runtime class
class Runtime : public Object<detail::RuntimeImpl> {
 public:
  Runtime(detail::Impl base, const std::string& libraryPath);
  using Object::Object;

  Devices getDevices() const;
  Device getDevice(nxs_uint deviceId) const;

  // Get Runtime Property Value
  std::optional<Property> getProperty(nxs_int prop) const override;
};

typedef Objects<Runtime> Runtimes;

}  // namespace nexus

#endif  // NEXUS_RUNTIME_H
