#ifndef NEXUS_OBJECT_H
#define NEXUS_OBJECT_H

#include <nexus-api.h>
#include <nexus/property.h>

#include <memory>
#include <optional>
#include <vector>

namespace nexus {

namespace detail {

// All Actual objects need an owner (except System)
// + and ID within the owner
class Impl {
 public:
  Impl(Impl *_owner = nullptr, nxs_int _id = -1, nxs_uint _settings = 0)
      : owner(_owner), id(_id), settings(_settings) {}
  virtual ~Impl() {}

  nxs_int getId() const { return id; }

  nxs_uint getSettings() const { return settings; }

 protected:
  // Only the derived class can access
  template <typename T = Impl>
  T *getParent() const {
    return dynamic_cast<T *>(owner);
  }

  template <typename T>
  T *getParentOfType() const {
    if (auto *par = dynamic_cast<T *>(owner)) return par;
    if (owner) return owner->getParentOfType<T>();
    return nullptr;
  }

 private:
  Impl *owner;
  nxs_int id;
  nxs_uint settings;
};

}  // namespace detail

// Facade base-class
template <typename Timpl>
class Object {
  // set of runtimes
  typedef std::shared_ptr<Timpl> ImplRef;
  ImplRef impl;

  const detail::Impl *getImpl() const {
    return reinterpret_cast<const detail::Impl *>(impl.get());
  }

 public:
  template <typename... Args>
  Object(detail::Impl owner, Args... args)
      : impl(std::make_shared<Timpl>(owner, args...)) {}

  template <typename... Args>
  Object(Args... args) : impl(std::make_shared<Timpl>(args...)) {}

  // Empty CTor - assumes Impl doesn't have an empty CTOR
  Object() = default;

  Object(const Object& other) : impl(other.impl) {}

  virtual ~Object() {}

  operator bool() const { return nxs_valid_id(getId()); }

  void release() { impl.clear(); }

  nxs_int getId() const {
    if (auto *impl = getImpl()) return impl->getId();
    return NXS_InvalidObject;
  }
  nxs_uint getSettings() const {
    if (auto *impl = getImpl()) return impl->getSettings();
    return 0;
  }

  virtual std::optional<Property> getProperty(nxs_int prop) const = 0;

  template <typename T>
  const T getProp(nxs_int prop) const {
    if (auto val = getProperty(prop)) return val->template getValue<T>();
    return T();
  }

 protected:
  ImplRef get() const { return impl; }
};

// Storage of vector of objects
template <typename Tobject>
class Objects {
  // set of runtimes
  typedef std::vector<Tobject> ObjectVec;
  std::shared_ptr<ObjectVec> objects;

 public:
  Objects() : objects(std::make_shared<ObjectVec>()) {}

  operator bool() const { return objects && !objects->empty(); }
  bool operator==(const Objects &that) const { return objects == that.objects; }
  bool operator!=(const Objects &that) const { return objects != that.objects; }

  nxs_int size() const { return objects->size(); }
  bool empty() const { return objects->empty(); }

  nxs_int add(Tobject obj) {
    objects->push_back(obj);
    return objects->size() - 1;
  }
  Tobject get(nxs_int idx) const {
    if (idx >= 0 && idx < objects->size()) return (*objects)[idx];
    return Tobject();
  }
  Tobject operator[](nxs_int idx) const { return get(idx); }

  void clear() { objects->clear(); }

  typename ObjectVec::iterator begin() const { return objects->begin(); }
  typename ObjectVec::iterator end() const { return objects->end(); }
};

#define NEXUS_OBJ_MCALL(RET, FUNC, ...) \
  if (auto obj = get()) { \
    return obj->FUNC(__VA_ARGS__); \
  } \
  return RET

}  // namespace nexus

#endif  // NEXUS_OBJECT_H
