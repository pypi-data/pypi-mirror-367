#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* matreg.c */
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
#define matsettype_ MATSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsettype_ matsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgettype_ MATGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgettype_ matgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetvectype_ MATGETVECTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetvectype_ matgetvectype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetvectype_ MATSETVECTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetvectype_ matsetvectype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matregisterrootname_ MATREGISTERROOTNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matregisterrootname_ matregisterrootname
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matsettype_(Mat mat,char *matype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for matype */
  FIXCHAR(matype,cl0,_cltmp0);
*ierr = MatSetType(
	(Mat)PetscToPointer((mat) ),_cltmp0);
  FREECHAR(matype,_cltmp0);
}
PETSC_EXTERN void  matgettype_(Mat mat,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatGetType(
	(Mat)PetscToPointer((mat) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  matgetvectype_(Mat mat,char *vtype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
*ierr = MatGetVecType(
	(Mat)PetscToPointer((mat) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for vtype */
*ierr = PetscStrncpy(vtype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, vtype, cl0);
}
PETSC_EXTERN void  matsetvectype_(Mat mat,char *vtype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mat);
/* insert Fortran-to-C conversion for vtype */
  FIXCHAR(vtype,cl0,_cltmp0);
*ierr = MatSetVecType(
	(Mat)PetscToPointer((mat) ),_cltmp0);
  FREECHAR(vtype,_cltmp0);
}
PETSC_EXTERN void  matregisterrootname_( char rname[], char sname[], char mname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1, PETSC_FORTRAN_CHARLEN_T cl2)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
  char *_cltmp2 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for rname */
  FIXCHAR(rname,cl0,_cltmp0);
/* insert Fortran-to-C conversion for sname */
  FIXCHAR(sname,cl1,_cltmp1);
/* insert Fortran-to-C conversion for mname */
  FIXCHAR(mname,cl2,_cltmp2);
*ierr = MatRegisterRootName(_cltmp0,_cltmp1,_cltmp2);
  FREECHAR(rname,_cltmp0);
  FREECHAR(sname,_cltmp1);
  FREECHAR(mname,_cltmp2);
}
#if defined(__cplusplus)
}
#endif
