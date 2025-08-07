#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pythonmat.c */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpythonsettype_ MATPYTHONSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpythonsettype_ matpythonsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpythongettype_ MATPYTHONGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpythongettype_ matpythongettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matpythoncreate_ MATPYTHONCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matpythoncreate_ matpythoncreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matpythonsettype_(Mat mat, char pyname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for pyname */
  FIXCHAR(pyname,cl0,_cltmp0);
*ierr = MatPythonSetType(
	(Mat)PetscToPointer((mat) ),_cltmp0);
  FREECHAR(pyname,_cltmp0);
}
PETSC_EXTERN void  matpythongettype_(Mat mat, char *pyname, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatPythonGetType(
	(Mat)PetscToPointer((mat) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for pyname */
*ierr = PetscStrncpy(pyname, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, pyname, cl0);
}
PETSC_EXTERN void  matpythoncreate_(MPI_Fint * comm,PetscInt *m,PetscInt *n,PetscInt *M,PetscInt *N, char pyname[],Mat *A, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
/* insert Fortran-to-C conversion for pyname */
  FIXCHAR(pyname,cl0,_cltmp0);
*ierr = MatPythonCreate(
	MPI_Comm_f2c(*(comm)),*m,*n,*M,*N,_cltmp0,A);
  FREECHAR(pyname,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
