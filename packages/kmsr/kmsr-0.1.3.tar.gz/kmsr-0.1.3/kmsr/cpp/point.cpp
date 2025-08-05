#include <iostream>
#include <sstream>

#include "../header/point.h"

Point::Point(std::vector<double> coords) : coordinates(coords) {}
Point::Point(int dimension) : coordinates(dimension, 0.0) {}
Point::Point(std::vector<double> coords, int pos) : coordinates(coords), position(pos) {}

double Point::distanceTo(const Point &other) const
{
  if (coordinates.size() != other.coordinates.size())
  {
    throw std::invalid_argument("The points should have the same dimensions!");
  }
  double sum = 0.0;
  for (size_t i = 0; i < coordinates.size(); i++)
  {
    sum += (coordinates[i] - other.coordinates[i]) *
           (coordinates[i] - other.coordinates[i]);
  }
  return std::sqrt(sum);
}

double Point::distance(const Point &p1, const Point &p2)
{
  return p1.distanceTo(p2);
}

bool Point::operator<(const Point &other) const
{
  return coordinates < other.coordinates;
}

bool Point::operator==(const Point &other) const
{
  if (coordinates.size() != other.coordinates.size())
  {
    return false;
  }
  for (size_t i = 0; i < coordinates.size(); i++)
  {
    if (coordinates[i] != other.coordinates[i])
    {
      return false;
    }
  }
  return true;
}

bool Point::operator!=(const Point &other) const { return !(*this == other); }

Point Point::operator+(const Point &other) const
{
  if (coordinates.size() != other.coordinates.size())
  {
    throw std::invalid_argument("The points should have the same dimensions!");
  }
  std::vector<double> result_coords(coordinates.size());
  for (size_t i = 0; i < coordinates.size(); i++)
  {
    result_coords[i] = coordinates[i] + other.coordinates[i];
  }
  return Point(result_coords);
}

Point Point::operator*(double scalar) const
{
  std::vector<double> result_coords(coordinates.size());
  for (size_t i = 0; i < coordinates.size(); i++)
  {
    result_coords[i] = coordinates[i] * scalar;
  }
  return Point(result_coords);
}

std::string Point::print() const
{
  std::stringstream tmp;
  tmp << "[" << position << "] ";
  tmp << "(";
  for (size_t i = 0; i < coordinates.size(); i++)
  {
    tmp << coordinates[i];
    if (i < coordinates.size() - 1)
    {
      tmp << ", ";
    }
  }
  tmp << ")";
  return tmp.str();
}
