#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* block.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscis.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isblocksetindices_ ISBLOCKSETINDICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isblocksetindices_ isblocksetindices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscreateblock_ ISCREATEBLOCK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscreateblock_ iscreateblock
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isblockgetlocalsize_ ISBLOCKGETLOCALSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isblockgetlocalsize_ isblockgetlocalsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isblockgetsize_ ISBLOCKGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isblockgetsize_ isblockgetsize
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  isblocksetindices_(IS is,PetscInt *bs,PetscInt *n, PetscInt idx[],PetscCopyMode *mode, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLINTEGER(idx);
*ierr = ISBlockSetIndices(
	(IS)PetscToPointer((is) ),*bs,*n,idx,*mode);
}
PETSC_EXTERN void  iscreateblock_(MPI_Fint * comm,PetscInt *bs,PetscInt *n, PetscInt idx[],PetscCopyMode *mode,IS *is, int *ierr)
{
CHKFORTRANNULLINTEGER(idx);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = ISCreateBlock(
	MPI_Comm_f2c(*(comm)),*bs,*n,idx,*mode,is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  isblockgetlocalsize_(IS is,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLINTEGER(size);
*ierr = ISBlockGetLocalSize(
	(IS)PetscToPointer((is) ),size);
}
PETSC_EXTERN void  isblockgetsize_(IS is,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLINTEGER(size);
*ierr = ISBlockGetSize(
	(IS)PetscToPointer((is) ),size);
}
#if defined(__cplusplus)
}
#endif
