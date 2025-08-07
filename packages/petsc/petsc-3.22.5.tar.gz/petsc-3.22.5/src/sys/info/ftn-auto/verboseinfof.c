#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* verboseinfo.c */
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

#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinfoenabled_ PETSCINFOENABLED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinfoenabled_ petscinfoenabled
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinfoallow_ PETSCINFOALLOW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinfoallow_ petscinfoallow
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinfosetfile_ PETSCINFOSETFILE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinfosetfile_ petscinfosetfile
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinfogetclass_ PETSCINFOGETCLASS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinfogetclass_ petscinfogetclass
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinfogetinfo_ PETSCINFOGETINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinfogetinfo_ petscinfogetinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinfoprocessclass_ PETSCINFOPROCESSCLASS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinfoprocessclass_ petscinfoprocessclass
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinfosetfiltercommself_ PETSCINFOSETFILTERCOMMSELF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinfosetfiltercommself_ petscinfosetfiltercommself
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinfosetfromoptions_ PETSCINFOSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinfosetfromoptions_ petscinfosetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinfodestroy_ PETSCINFODESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinfodestroy_ petscinfodestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinfodeactivateclass_ PETSCINFODEACTIVATECLASS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinfodeactivateclass_ petscinfodeactivateclass
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscinfoactivateclass_ PETSCINFOACTIVATECLASS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscinfoactivateclass_ petscinfoactivateclass
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscinfoenabled_(PetscClassId *classid,PetscBool *enabled, int *ierr)
{
*ierr = PetscInfoEnabled(*classid,enabled);
}
PETSC_EXTERN void  petscinfoallow_(PetscBool *flag, int *ierr)
{
*ierr = PetscInfoAllow(*flag);
}
PETSC_EXTERN void  petscinfosetfile_( char filename[], char mode[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for filename */
  FIXCHAR(filename,cl0,_cltmp0);
/* insert Fortran-to-C conversion for mode */
  FIXCHAR(mode,cl1,_cltmp1);
*ierr = PetscInfoSetFile(_cltmp0,_cltmp1);
  FREECHAR(filename,_cltmp0);
  FREECHAR(mode,_cltmp1);
}
PETSC_EXTERN void  petscinfogetclass_( char classname[],PetscBool *found, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for classname */
  FIXCHAR(classname,cl0,_cltmp0);
*ierr = PetscInfoGetClass(_cltmp0,found);
  FREECHAR(classname,_cltmp0);
}
PETSC_EXTERN void  petscinfogetinfo_(PetscBool *infoEnabled,PetscBool *classesSet,PetscBool *exclude,PetscBool *locked,PetscInfoCommFlag *commSelfFlag, int *ierr)
{
*ierr = PetscInfoGetInfo(infoEnabled,classesSet,exclude,locked,commSelfFlag);
}
PETSC_EXTERN void  petscinfoprocessclass_( char classname[],PetscInt *numClassID, PetscClassId classIDs[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for classname */
  FIXCHAR(classname,cl0,_cltmp0);
*ierr = PetscInfoProcessClass(_cltmp0,*numClassID,classIDs);
  FREECHAR(classname,_cltmp0);
}
PETSC_EXTERN void  petscinfosetfiltercommself_(PetscInfoCommFlag *commSelfFlag, int *ierr)
{
*ierr = PetscInfoSetFilterCommSelf(*commSelfFlag);
}
PETSC_EXTERN void  petscinfosetfromoptions_(PetscOptions options, int *ierr)
{
CHKFORTRANNULLOBJECT(options);
*ierr = PetscInfoSetFromOptions(
	(PetscOptions)PetscToPointer((options) ));
}
PETSC_EXTERN void  petscinfodestroy_(int *ierr)
{
*ierr = PetscInfoDestroy();
}
PETSC_EXTERN void  petscinfodeactivateclass_(PetscClassId *classid, int *ierr)
{
*ierr = PetscInfoDeactivateClass(*classid);
}
PETSC_EXTERN void  petscinfoactivateclass_(PetscClassId *classid, int *ierr)
{
*ierr = PetscInfoActivateClass(*classid);
}
#if defined(__cplusplus)
}
#endif
