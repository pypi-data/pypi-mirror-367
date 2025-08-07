#ifndef BITMAP_CUBICAL_COMPLEX_BASE_H_
#define BITMAP_CUBICAL_COMPLEX_BASE_H_

#include "counter.h"
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <algorithm>
#include <iterator>
#include <limits>
#include <utility>
#include <stdexcept>
#include <cstddef>


// Overload operator<< to print vectors nicely
template <typename T>
std::ostream& operator<<(std::ostream& os, const std::vector<T>& vec) {
    os << "[";
    for (size_t i = 0; i < vec.size(); ++i) {
        os << vec[i];
        if (i + 1 != vec.size()) os << ", ";
    }
    os << "]";
    return os;
}



template<typename T>
T get_default_cell_value(unsigned /*unused*/ = 1);

template<>
inline double get_default_cell_value<double>(unsigned) {
    return std::numeric_limits<double>::infinity();
}

template<>
inline std::vector<double> get_default_cell_value<std::vector<double>>(unsigned vec_size) {
    return std::vector<double>(vec_size, std::numeric_limits<double>::infinity());
}


/**
 * @brief Cubical complex represented as a bitmap, class with basic implementation.
 * @ingroup cubical_complex
 * @details This is a class implementing a basic bitmap data structure to store cubical complexes.
 * It implements only the most basic subroutines.
 * The idea of the bitmap is the following. Our aim is to have a memory efficient
 * data structure to store d-dimensional cubical complex
 * C being a cubical decomposition
 * of a rectangular region of a space. This is achieved by storing C as a
 * vector of bits (this is where the name 'bitmap' came from).
 * Each cell is represented by a single
 * bit (in case of black and white bitmaps, or by a single element of a type T
 * (here T is a filtration type of a bitmap, typically a double).
 * All the informations needed for homology and
 * persistent homology computations (like dimension of a cell, boundary and
 * coboundary elements of a cell, are then obtained from the
 * position of the element in C.
 * The default filtration used in this implementation is the lower star filtration.
 */
template <typename T>
class Bitmap_cubical_complex_base {
 public:
  typedef T filtration_type;
  
  /**
  *Default constructor
  **/
  Bitmap_cubical_complex_base() : total_number_of_cells(0) {}  

  Bitmap_cubical_complex_base(const std::vector<unsigned>& dimensions, const std::vector<T>& top_dimensional_cells);

  /**
   * Destructor of the Bitmap_cubical_complex_base class.
   **/
  virtual ~Bitmap_cubical_complex_base() {}

  /**
   * The functions get_boundary_of_a_cell, get_coboundary_of_a_cell, get_dimension_of_a_cell
   * and get_cell_data are the basic
   * functions that compute boundary / coboundary / dimension and the filtration
   * value form a position of a cell in the structure of a bitmap. The input parameter of all of those function is a
   * non-negative integer, indicating a position of a cube in the data structure.
   * In the case of functions that compute (co)boundary, the output is a vector if non-negative integers pointing to
   * the positions of (co)boundary element of the input cell.
   * The boundary elements are guaranteed to be returned so that the
   * incidence coefficients of boundary elements are alternating.
   */
  virtual inline std::vector<std::size_t> get_boundary_of_a_cell(std::size_t cell) const;
  /**
   * The functions get_coboundary_of_a_cell, get_coboundary_of_a_cell,
   * get_dimension_of_a_cell and get_cell_data are the basic
   * functions that compute boundary / coboundary / dimension and the filtration
   * value form a position of a cell in the structure of a bitmap.
   * The input parameter of all of those function is a non-negative integer,
   * indicating a position of a cube in the data structure.
   * In the case of functions that compute (co)boundary, the output is a vector if
   * non-negative integers pointing to the
   * positions of (co)boundary element of the input cell.
   * Note that unlike in the case of boundary, over here the elements are
   * not guaranteed to be returned with alternating incidence numbers.
   *
   **/
  virtual inline std::vector<std::size_t> get_coboundary_of_a_cell(std::size_t cell) const;


  /**
  * In the case of get_dimension_of_a_cell function, the output is a non-negative integer
  * indicating the dimension of a cell.
  * Note that unlike in the case of boundary, over here the elements are
  * not guaranteed to be returned with alternating incidence numbers.
  * To compute incidence between cells use compute_incidence_between_cells
  * procedure
  **/
  inline unsigned get_dimension_of_a_cell(std::size_t cell) const;

  /**
   * In the case of get_cell_data, the output parameter is a reference to the value of a cube in a given position.
   * This allows reading and changing the value of filtration. Note that if the value of a filtration is changed, the
   * code do not check if we have a filtration or not. i.e. it do not check if the value of a filtration of a cell is
   * not smaller than the value of a filtration of its boundary and not greater than the value of its coboundary.
   **/
  inline T& get_cell_data(std::size_t cell);

  /**
   * Typical input used to construct a baseBitmap class is a filtration given at the top dimensional cells.
   * Then, there are a few ways one can pick the filtration of lower dimensional
   * cells. The most typical one is by so called lower star filtration. This function is always called by any
   * constructor which takes the top dimensional cells. If you use such a constructor,
   * then there is no need to call this function. Call it only if you are putting the filtration
   * of the cells by your own (for instance by using Top_dimensional_cells_iterator).
   **/
  void impose_lower_star_filtration();  // assume that top dimensional cells are already set.

  /**
   * Returns dimension of a complex.
   **/
  inline unsigned dimension() const { return sizes.size(); }

  /**
   * Returns number of all cubes in the data structure.
   **/
  inline std::size_t size() const { return this->data.size(); }


    /**
   * @brief Iterator through top dimensional cells of the complex. The cells appear in order they are stored
   * in the structure (i.e. in lexicographical order)
   **/
  class Top_dimensional_cells_iterator : std::iterator<std::input_iterator_tag, T> {
   public:
    Top_dimensional_cells_iterator(Bitmap_cubical_complex_base& b) : b(b) {
      this->counter = std::vector<std::size_t>(b.dimension());
      // std::fill( this->counter.begin() , this->counter.end() , 0 );
    }

    Top_dimensional_cells_iterator operator++() {
      // first find first element of the counter that can be increased:
      std::size_t dim = 0;
      while ((dim != this->b.dimension()) && (this->counter[dim] == this->b.sizes[dim] - 1)) ++dim;

      if (dim != this->b.dimension()) {
        ++this->counter[dim];
        for (std::size_t i = 0; i != dim; ++i) {
          this->counter[i] = 0;
        }
      } else {
        ++this->counter[0];
      }
      return *this;
    }

    Top_dimensional_cells_iterator operator++(int) {
      Top_dimensional_cells_iterator result = *this;
      ++(*this);
      return result;
    }

    Top_dimensional_cells_iterator& operator=(const Top_dimensional_cells_iterator& rhs) {
      this->counter = rhs.counter;
      this->b = rhs.b;
      return *this;
    }

    bool operator==(const Top_dimensional_cells_iterator& rhs) const {
      if (&this->b != &rhs.b) return false;
      if (this->counter.size() != rhs.counter.size()) return false;
      for (std::size_t i = 0; i != this->counter.size(); ++i) {
        if (this->counter[i] != rhs.counter[i]) return false;
      }
      return true;
    }

    bool operator!=(const Top_dimensional_cells_iterator& rhs) const { return !(*this == rhs); }

    /*
     * The operator * returns position of a cube in the structure of cubical complex. This position can be then used as
     * an argument of the following functions:
     * get_boundary_of_a_cell, get_coboundary_of_a_cell, get_dimension_of_a_cell to get information about the cell
     * boundary and coboundary and dimension
     * and in function get_cell_data to get a filtration of a cell.
     */
    std::size_t operator*() { return this->compute_index_in_bitmap(); }

    std::size_t compute_index_in_bitmap() const {
      std::size_t index = 0;
      for (std::size_t i = 0; i != this->counter.size(); ++i) {
        index += (2 * this->counter[i] + 1) * this->b.multipliers[i];
      }
      return index;
    }

    void print_counter() const {
      for (std::size_t i = 0; i != this->counter.size(); ++i) {
        std::clog << this->counter[i] << " ";
      }
    }
    friend class Bitmap_cubical_complex_base;

   protected:
    std::vector<std::size_t> counter;
    Bitmap_cubical_complex_base& b;
  };

  /**
   * Function returning a Top_dimensional_cells_iterator to the first top dimensional cell of the bitmap.
   **/
  Top_dimensional_cells_iterator top_dimensional_cells_iterator_begin() {
    Top_dimensional_cells_iterator a(*this);
    return a;
  }

  /**
   * Function returning a Top_dimensional_cells_iterator to the last top dimensional cell of the bitmap.
   **/
  Top_dimensional_cells_iterator top_dimensional_cells_iterator_end() {
    Top_dimensional_cells_iterator a(*this);
    for (std::size_t i = 0; i != this->dimension(); ++i) {
      a.counter[i] = this->sizes[i] - 1;
    }
    a.counter[0]++;
    return a;
  }

  /**
   * @brief Top_dimensional_cells_iterator_range class provides ranges for Top_dimensional_cells_iterator_range
   **/
  class Top_dimensional_cells_range {
   public:
    Top_dimensional_cells_range(Bitmap_cubical_complex_base* b) : b(b) {}

    Top_dimensional_cells_iterator begin() { return b->top_dimensional_cells_iterator_begin(); }

    Top_dimensional_cells_iterator end() { return b->top_dimensional_cells_iterator_end(); }

   private:
    Bitmap_cubical_complex_base<T>* b;
  };



 protected:
  std::vector<unsigned> sizes;
  std::vector<unsigned> multipliers;
  std::vector<T> data;
  std::size_t total_number_of_cells;
  unsigned filtration_vector_size = 1; // default is scalar filtration


  void set_up_containers(const std::vector<unsigned>& sizes, const unsigned & filtration_vector_size) {

    unsigned multiplier = 1;
    for (std::size_t i = 0; i != sizes.size(); ++i) {
      this->sizes.push_back(sizes[i]);
      this->multipliers.push_back(multiplier);
      multiplier *= 2 * sizes[i] + 1;
    }
    this->data = std::vector<T>(multiplier, get_default_cell_value<T>(filtration_vector_size));
    this->total_number_of_cells = multiplier;
  }

  std::size_t compute_position_in_bitmap(const std::vector<unsigned>& counter) {
    std::size_t position = 0;
    for (std::size_t i = 0; i != this->multipliers.size(); ++i) {
      position += this->multipliers[i] * counter[i];
    }
    return position;
  }

  std::vector<unsigned> compute_counter_for_given_cell(std::size_t cell) const {
    std::vector<unsigned> counter;
    counter.reserve(this->sizes.size());
    for (std::size_t dim = this->sizes.size(); dim != 0; --dim) {
      counter.push_back(cell / this->multipliers[dim - 1]);
      cell = cell % this->multipliers[dim - 1];
    }
    std::reverse(counter.begin(), counter.end());
    return counter;
  }
  void read_perseus_style_file(const char* perseus_style_file);
  void setup_bitmap_based_on_top_dimensional_cells_list(const std::vector<unsigned>& sizes_in_following_directions,
                                                        const std::vector<T>& top_dimensional_cells);
  Bitmap_cubical_complex_base(const char* perseus_style_file, std::vector<bool> directions);
  Bitmap_cubical_complex_base(const std::vector<unsigned>& sizes, std::vector<bool> directions);
  Bitmap_cubical_complex_base(const std::vector<unsigned>& dimensions, const std::vector<T>& top_dimensional_cells,
                              std::vector<bool> directions);
};

template <typename K>
std::ostream& operator<<(std::ostream& out, const Bitmap_cubical_complex_base<K>& b) {
  for (typename Bitmap_cubical_complex_base<K>::all_cells_const_iterator it = b.all_cells_const_begin();
       it != b.all_cells_const_end(); ++it) {
    out << *it << " ";
  }
  return out;
}


template <typename T>
void Bitmap_cubical_complex_base<T>::setup_bitmap_based_on_top_dimensional_cells_list(
    const std::vector<unsigned>& sizes_in_following_directions, const std::vector<T>& top_dimensional_cells) {
  this->set_up_containers(sizes_in_following_directions, top_dimensional_cells[0].size());

  std::size_t number_of_top_dimensional_elements = 1;
  for (std::size_t i = 0; i != sizes_in_following_directions.size(); ++i) {
    number_of_top_dimensional_elements *= sizes_in_following_directions[i];
  }
  if (number_of_top_dimensional_elements != top_dimensional_cells.size()) {
    std::cerr << "Error in constructor Bitmap_cubical_complex_base ( std::vector<std::size_t> "
              << "sizes_in_following_directions, std::vector<T> top_dimensional_cells ). Number of top dimensional "
              << "elements that follow from sizes_in_following_directions vector is different than the size of "
              << "top_dimensional_cells vector."
              << std::endl;
    throw(
        "Error in constructor Bitmap_cubical_complex_base( std::vector<std::size_t> sizes_in_following_directions,"
        "std::vector<T> top_dimensional_cells ). Number of top dimensional elements that follow from "
        "sizes_in_following_directions vector is different than the size of top_dimensional_cells vector.");
  }

  Bitmap_cubical_complex_base<T>::Top_dimensional_cells_iterator it(*this);
  std::size_t index = 0;
  for (it = this->top_dimensional_cells_iterator_begin(); it != this->top_dimensional_cells_iterator_end(); ++it) {
    this->get_cell_data(*it) = top_dimensional_cells[index];
    ++index;
  }
  this->impose_lower_star_filtration();
}



template <typename T>
Bitmap_cubical_complex_base<T>::Bitmap_cubical_complex_base(const std::vector<unsigned>& sizes_in_following_directions,
                                                            const std::vector<T>& top_dimensional_cells) {
  this->setup_bitmap_based_on_top_dimensional_cells_list(sizes_in_following_directions, top_dimensional_cells);
}


template <typename T>
Bitmap_cubical_complex_base<T>::Bitmap_cubical_complex_base(const std::vector<unsigned>& sizes,
                                                            std::vector<bool> directions) {
  // this constructor is here just for compatibility with a class that creates cubical complexes with periodic boundary
  // conditions.
  // It ignores the last parameter of the function.
  this->set_up_containers(sizes);
}

template <typename T>
Bitmap_cubical_complex_base<T>::Bitmap_cubical_complex_base(const std::vector<unsigned>& dimensions,
                                                            const std::vector<T>& top_dimensional_cells,
                                                            std::vector<bool> directions) {
  // this constructor is here just for compatibility with a class that creates cubical complexes with periodic boundary
  // conditions.
  // It ignores the last parameter of the function.
  this->setup_bitmap_based_on_top_dimensional_cells_list(dimensions, top_dimensional_cells);
}


template <typename T>
std::vector<std::size_t> Bitmap_cubical_complex_base<T>::get_boundary_of_a_cell(std::size_t cell) const {
  std::vector<std::size_t> boundary_elements;

  // Speed traded of for memory. Check if it is better in practice.
  boundary_elements.reserve(this->dimension() * 2);

  std::size_t sum_of_dimensions = 0;
  std::size_t cell1 = cell;
  for (std::size_t i = this->multipliers.size(); i != 0; --i) {
    unsigned position = cell1 / this->multipliers[i - 1];
    if (position % 2 == 1) {
      if (sum_of_dimensions % 2) {
        boundary_elements.push_back(cell + this->multipliers[i - 1]);
        boundary_elements.push_back(cell - this->multipliers[i - 1]);
      } else {
        boundary_elements.push_back(cell - this->multipliers[i - 1]);
        boundary_elements.push_back(cell + this->multipliers[i - 1]);
      }
      ++sum_of_dimensions;
    }
    cell1 = cell1 % this->multipliers[i - 1];
  }

  return boundary_elements;
}

template <typename T>
std::vector<std::size_t> Bitmap_cubical_complex_base<T>::get_coboundary_of_a_cell(std::size_t cell) const {
  std::vector<unsigned> counter = this->compute_counter_for_given_cell(cell);
  std::vector<std::size_t> coboundary_elements;
  std::size_t cell1 = cell;
  for (std::size_t i = this->multipliers.size(); i != 0; --i) {
    unsigned position = cell1 / this->multipliers[i - 1];
    if (position % 2 == 0) {
      if ((cell > this->multipliers[i - 1]) && (counter[i - 1] != 0)) {
        coboundary_elements.push_back(cell - this->multipliers[i - 1]);
      }
      if ((cell + this->multipliers[i - 1] < this->data.size()) && (counter[i - 1] != 2 * this->sizes[i - 1])) {
        coboundary_elements.push_back(cell + this->multipliers[i - 1]);
      }
    }
    cell1 = cell1 % this->multipliers[i - 1];
  }
  return coboundary_elements;
}

template <typename T>
unsigned Bitmap_cubical_complex_base<T>::get_dimension_of_a_cell(std::size_t cell) const {
  bool dbg = false;
  if (dbg) std::clog << "\n\n\n Computing position o a cell of an index : " << cell << std::endl;
  unsigned dimension = 0;
  for (std::size_t i = this->multipliers.size(); i != 0; --i) {
    unsigned position = cell / this->multipliers[i - 1];

    if (dbg) {
      std::clog << "i-1 :" << i - 1 << std::endl;
      std::clog << "cell : " << cell << std::endl;
      std::clog << "position : " << position << std::endl;
      std::clog << "multipliers[" << i - 1 << "] = " << this->multipliers[i - 1] << std::endl;
    }

    if (position % 2 == 1) {
      if (dbg) std::clog << "Nonzero length in this direction \n";
      dimension++;
    }
    cell = cell % this->multipliers[i - 1];
  }
  return dimension;
}

template <typename T>
inline T& Bitmap_cubical_complex_base<T>::get_cell_data(std::size_t cell) {
  return this->data[cell];
}

template <typename T>
void Bitmap_cubical_complex_base<T>::impose_lower_star_filtration() {
  bool dbg = false;

  // this vector will be used to check which elements have already been taken care of in imposing lower star filtration
  std::vector<bool> is_this_cell_considered(this->data.size(), false);

  std::size_t size_to_reserve = 1;
  for (std::size_t i = 0; i != this->multipliers.size(); ++i) {
    size_to_reserve *= (std::size_t)((this->multipliers[i] - 1) / 2);
  }

  std::vector<std::size_t> indices_to_consider;
  indices_to_consider.reserve(size_to_reserve);
  // we assume here that we already have a filtration on the top dimensional cells and
  // we have to extend it to lower ones.
  typename Bitmap_cubical_complex_base<T>::Top_dimensional_cells_iterator it(*this);
  for (it = this->top_dimensional_cells_iterator_begin(); it != this->top_dimensional_cells_iterator_end(); ++it) {
    indices_to_consider.push_back(it.compute_index_in_bitmap());
  }

  while (indices_to_consider.size()) {
    if (dbg) {
      std::clog << "indices_to_consider in this iteration \n";
      for (std::size_t i = 0; i != indices_to_consider.size(); ++i) {
        std::clog << indices_to_consider[i] << "  ";
      }
    }
    std::vector<std::size_t> new_indices_to_consider;

    for (std::size_t i = 0; i != indices_to_consider.size(); ++i)
    {
      std::vector<std::size_t> bd = this->get_boundary_of_a_cell(indices_to_consider[i]);
      for (std::size_t boundaryIt = 0; boundaryIt != bd.size(); ++boundaryIt)
      {
        if (dbg) {
          std::clog << "filtration of a cell : " << bd[boundaryIt] << " is : " << this->data[bd[boundaryIt]]
                    << " while of a cell: " << indices_to_consider[i] << " is: " << this->data[indices_to_consider[i]]
                    << std::endl;
        }
        for ( size_t v = 0 ; v != this->data[bd[boundaryIt]].size() ; ++v )
        {
          if (this->data[bd[boundaryIt]][v] > this->data[indices_to_consider[i]][v])
            {
              this->data[bd[boundaryIt]][v] = this->data[indices_to_consider[i]][v];
              if (dbg) {
                std::clog << "Setting the value of a cell : " << bd[boundaryIt]
                      << " to : " << this->data[indices_to_consider[i]] << std::endl;
              }
            }
        }
        if (is_this_cell_considered[bd[boundaryIt]] == false) {
          new_indices_to_consider.push_back(bd[boundaryIt]);
          is_this_cell_considered[bd[boundaryIt]] = true;
        }
      }
    }
    indices_to_consider.swap(new_indices_to_consider);
  }
}






template <typename T>
bool compareFirstElementsOfTuples(const std::pair<std::pair<T, std::size_t>, char>& first,
                                  const std::pair<std::pair<T, std::size_t>, char>& second) {
  if (first.first.first < second.first.first) {
    return true;
  } else {
    if (first.first.first > second.first.first) {
      return false;
    }
    // in this case first.first.first == second.first.first, so we need to compare dimensions
    return first.second < second.second;
  }
}

#endif  // BITMAP_CUBICAL_COMPLEX_BASE_H_
